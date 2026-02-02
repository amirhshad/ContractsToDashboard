"""Vercel serverless API using basic HTTP handler."""

from http.server import BaseHTTPRequestHandler
import json
import os
import re
from urllib.parse import urlparse, parse_qs
import base64

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Constants
MAX_FILES_PER_CONTRACT = 5


def get_supabase_client(use_service_key=True):
    """Get Supabase client."""
    from supabase import create_client
    key = SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY
    return create_client(SUPABASE_URL, key)


def get_user_from_token(token):
    """Get user ID from JWT token."""
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    user = supabase.auth.get_user(token)
    return user.user.id


def parse_authorization(headers):
    """Extract token from Authorization header."""
    auth = headers.get("Authorization", headers.get("authorization", ""))
    if auth.startswith("Bearer "):
        return auth[7:]
    return auth


def parse_multipart_files(body, content_type):
    """Parse multipart form data and extract all files."""
    files = []
    metadata = None

    if "multipart/form-data" not in content_type:
        return files, metadata

    boundary = content_type.split("boundary=")[1].encode()
    parts = body.split(b"--" + boundary)

    for part in parts:
        if b"filename=" in part:
            # Extract headers
            header_end = part.find(b"\r\n\r\n")
            header = part[:header_end].decode()

            # Extract filename
            filename = None
            if 'filename="' in header:
                filename = header.split('filename="')[1].split('"')[0]

            # Extract field name to get document type
            field_name = "file"
            if 'name="' in header:
                field_name = header.split('name="')[1].split('"')[0]

            # Extract file content
            file_content = part[header_end + 4:].rstrip(b"\r\n--")

            if filename and file_content:
                files.append({
                    "filename": filename,
                    "content": file_content,
                    "field_name": field_name
                })

        # Check for files_metadata JSON field
        elif b'name="files_metadata"' in part:
            header_end = part.find(b"\r\n\r\n")
            content = part[header_end + 4:].rstrip(b"\r\n--")
            try:
                metadata = json.loads(content.decode())
            except:
                pass

    return files, metadata


# Unified extraction prompt
UNIFIED_EXTRACTION_PROMPT = """You are analyzing contract documents to extract structured data.
You may receive 1 to 5 related documents that together form a single contractual relationship.

IMPORTANT INSTRUCTIONS:
1. Analyze ALL provided documents together as one contract package
2. Extract a UNIFIED view combining information from all documents
3. If documents have conflicting terms, use the most recent/specific version
4. Amendments and SOWs typically override terms in the main agreement
5. Combine costs if multiple documents specify separate fees
6. Return ONLY valid JSON - no markdown, no explanation, no code blocks

REQUIRED OUTPUT FORMAT:
{
    "provider_name": "Company/service provider name (string or null)",
    "contract_nickname": "Short descriptive name for this specific contract (e.g., 'Car Insurance 2025', 'Office Lease', 'Netflix Subscription')",
    "contract_type": "insurance | utility | subscription | rental | saas | service | other",
    "monthly_cost": 0.00,
    "annual_cost": 0.00,
    "currency": "USD | EUR | GBP | CAD | AUD | JPY (detect from document)",
    "payment_frequency": "monthly | annual | quarterly | one-time | other",
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null",
    "auto_renewal": true | false | null,
    "cancellation_notice_days": 0,
    "key_terms": ["Important terms from ALL documents"],
    "parties": [
        {
            "name": "Full legal name of party",
            "role": "provider | client | insurer | insured | landlord | tenant | licensor | licensee | vendor | customer"
        }
    ],
    "risks": [
        {
            "title": "Short risk title",
            "description": "Why this is a risk and what to watch for",
            "severity": "high | medium | low"
        }
    ],
    "confidence": 0.0-1.0,
    "documents_analyzed": [
        {
            "filename": "original filename",
            "document_type": "main_agreement | sow | terms_conditions | amendment | addendum | exhibit | schedule | other",
            "summary": "One sentence summary"
        }
    ]
}

RISK CATEGORIES TO CHECK:
- Auto-renewal with short/no cancellation window
- Automatic price increases or escalation clauses
- Liability limitations that favor provider
- Data retention or privacy concerns
- Termination penalties or early exit fees
- Long lock-in periods without flexibility
- Unusual indemnification requirements
- Missing SLA or service guarantees
- Ambiguous scope of services

CONTRACT TYPE GUIDANCE:
- insurance: Health, auto, home, liability policies
- utility: Electric, gas, water, internet, phone
- subscription: Streaming, magazines, memberships
- rental: Real estate leases, equipment rental
- saas: Software subscriptions, cloud services
- service: Consulting, maintenance, professional services
- other: Anything that doesn't fit above

FIELD EXTRACTION RULES:
1. provider_name: Main company providing the service (not the customer)
2. parties: Extract ALL parties (usually 2+), identify their contractual roles
3. costs: Convert to numbers only (no currency symbols). Detect currency separately.
4. dates: Always use YYYY-MM-DD format
5. confidence: 0.9+ for clear documents, 0.6-0.8 for partial info, <0.6 for unclear
6. key_terms: Include renewal terms, limitations, important obligations, SLAs

Return ONLY the JSON object. Do not include any other text."""

# Currency normalization
CURRENCY_SYMBOL_MAP = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "C$": "CAD", "A$": "AUD"}
VALID_CURRENCIES = {"USD", "EUR", "GBP", "CAD", "AUD", "JPY"}


def normalize_currency(v):
    """Normalize currency symbols to codes."""
    if v is None:
        return "USD"
    v = str(v).strip()
    if v in CURRENCY_SYMBOL_MAP:
        return CURRENCY_SYMBOL_MAP[v]
    v_upper = v.upper()
    if v_upper in VALID_CURRENCIES:
        return v_upper
    return "USD"


def parse_extraction_result(raw_data: dict) -> dict:
    """Parse and normalize extraction result."""
    result = {
        "provider_name": raw_data.get("provider_name"),
        "contract_nickname": raw_data.get("contract_nickname"),
        "contract_type": raw_data.get("contract_type", "").lower() if raw_data.get("contract_type") else None,
        "monthly_cost": None,
        "annual_cost": None,
        "currency": normalize_currency(raw_data.get("currency")),
        "payment_frequency": raw_data.get("payment_frequency", "").lower() if raw_data.get("payment_frequency") else None,
        "start_date": raw_data.get("start_date"),
        "end_date": raw_data.get("end_date"),
        "auto_renewal": raw_data.get("auto_renewal"),
        "cancellation_notice_days": None,
        "key_terms": raw_data.get("key_terms", []),
        "parties": raw_data.get("parties", []),
        "risks": raw_data.get("risks", []),
        "confidence": 0.0,
        "documents_analyzed": raw_data.get("documents_analyzed", []),
    }

    # Parse numeric fields
    try:
        if raw_data.get("monthly_cost") is not None:
            result["monthly_cost"] = float(raw_data["monthly_cost"])
    except (ValueError, TypeError):
        pass

    try:
        if raw_data.get("annual_cost") is not None:
            result["annual_cost"] = float(raw_data["annual_cost"])
    except (ValueError, TypeError):
        pass

    try:
        if raw_data.get("cancellation_notice_days") is not None:
            result["cancellation_notice_days"] = int(raw_data["cancellation_notice_days"])
    except (ValueError, TypeError):
        pass

    try:
        result["confidence"] = float(raw_data.get("confidence", 0.0))
    except (ValueError, TypeError):
        result["confidence"] = 0.0

    # Normalize risk severities
    for risk in result["risks"]:
        if "severity" in risk:
            risk["severity"] = risk["severity"].lower() if isinstance(risk["severity"], str) else "medium"

    return result


class handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_json(self, message, status=400):
        """Send error JSON response."""
        self.send_json({"detail": message}, status)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        # Health endpoints
        if path in ["/api/", "/api/health"]:
            return self.send_json({"status": "healthy", "service": "Clausemate API"})

        # Auth required endpoints
        token = parse_authorization(dict(self.headers))
        if not token:
            return self.send_error_json("No token provided", 401)

        try:
            user_id = get_user_from_token(token)
        except Exception as e:
            return self.send_error_json(f"Invalid token: {str(e)}", 401)

        supabase = get_supabase_client()

        # Contracts endpoints
        if path == "/api/contracts":
            result = supabase.table("contracts").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            # Also fetch file counts for each contract
            contracts = result.data
            for contract in contracts:
                files_result = supabase.table("contract_files").select("id").eq("contract_id", contract["id"]).execute()
                contract["file_count"] = len(files_result.data)
            return self.send_json(contracts)

        if path == "/api/contracts/summary":
            from datetime import date, timedelta
            result = supabase.table("contracts").select("*").eq("user_id", user_id).execute()
            contracts = result.data

            total_monthly = 0
            total_annual = 0
            by_type = {}
            expiring_soon = 0
            auto_renewal_count = 0
            today = date.today()
            thirty_days = today + timedelta(days=30)

            for c in contracts:
                if c.get("monthly_cost"):
                    total_monthly += float(c["monthly_cost"])
                if c.get("annual_cost"):
                    total_annual += float(c["annual_cost"])
                ctype = c.get("contract_type") or "other"
                by_type[ctype] = by_type.get(ctype, 0) + 1
                if c.get("end_date"):
                    end = date.fromisoformat(c["end_date"])
                    if today <= end <= thirty_days:
                        expiring_soon += 1
                if c.get("auto_renewal"):
                    auto_renewal_count += 1

            return self.send_json({
                "total_contracts": len(contracts),
                "total_monthly_spend": total_monthly,
                "total_annual_spend": total_annual,
                "contracts_by_type": by_type,
                "expiring_soon": expiring_soon,
                "auto_renewal_count": auto_renewal_count,
            })

        # Contract files endpoint
        files_match = re.match(r"/api/contracts/([^/]+)/files", path)
        if files_match:
            contract_id = files_match.group(1)
            # Verify ownership
            contract = supabase.table("contracts").select("id").eq("id", contract_id).eq("user_id", user_id).execute()
            if not contract.data:
                return self.send_error_json("Contract not found", 404)

            files_result = supabase.table("contract_files").select("*").eq("contract_id", contract_id).order("display_order").execute()
            return self.send_json(files_result.data)

        # Single contract endpoint
        if path.startswith("/api/contracts/"):
            contract_id = path.split("/")[-1]
            result = supabase.table("contracts").select("*").eq("id", contract_id).eq("user_id", user_id).single().execute()
            if not result.data:
                return self.send_error_json("Contract not found", 404)

            # Also fetch files for this contract
            files_result = supabase.table("contract_files").select("*").eq("contract_id", contract_id).order("display_order").execute()
            result.data["files"] = files_result.data
            return self.send_json(result.data)

        # Recommendations
        if path == "/api/recommendations":
            result = supabase.table("recommendations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return self.send_json(result.data)

        return self.send_error_json("Not found", 404)

    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        token = parse_authorization(dict(self.headers))
        if not token:
            return self.send_error_json("No token provided", 401)

        try:
            user_id = get_user_from_token(token)
        except Exception as e:
            return self.send_error_json(f"Invalid token: {str(e)}", 401)

        supabase = get_supabase_client()

        # Upload extract - supports multiple files
        if path == "/api/upload/extract":
            try:
                import anthropic
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                content_type = self.headers.get("Content-Type", "")

                # Parse all files from multipart
                files, files_metadata = parse_multipart_files(body, content_type)

                if not files:
                    return self.send_error_json("No files uploaded", 400)

                if len(files) > MAX_FILES_PER_CONTRACT:
                    return self.send_error_json(f"Maximum {MAX_FILES_PER_CONTRACT} files allowed per contract", 400)

                # Build content array for Claude with all documents
                content = []

                for i, file_data in enumerate(files):
                    base64_content = base64.standard_b64encode(file_data["content"]).decode("utf-8")

                    # Add document
                    content.append({
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64_content
                        }
                    })

                    # Add context about the document
                    doc_type = "unknown"
                    if files_metadata and i < len(files_metadata):
                        doc_type = files_metadata[i].get("document_type", "other")
                    content.append({
                        "type": "text",
                        "text": f"Document {i+1}: {file_data['filename']} (Type: {doc_type})"
                    })

                # Add extraction prompt
                content.append({
                    "type": "text",
                    "text": UNIFIED_EXTRACTION_PROMPT
                })

                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

                response = client.messages.create(
                    model="claude-opus-4-5-20251101",
                    max_tokens=2048,
                    messages=[{
                        "role": "user",
                        "content": content
                    }]
                )

                result_text = response.content[0].text

                # Strip markdown code blocks if present
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                # Parse JSON and normalize
                raw_data = json.loads(result_text.strip())
                extraction = parse_extraction_result(raw_data)

                # Add file names
                extraction["file_names"] = [f["filename"] for f in files]

                return self.send_json(extraction)

            except Exception as e:
                import traceback
                error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                return self.send_error_json(f"Extraction failed: {error_details}", 500)

        # Upload confirm - supports multiple files
        if path == "/api/upload/confirm":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                content_type = self.headers.get("Content-Type", "")

                # Get query parameters
                params = {k: v[0] for k, v in query.items()}
                provider_name = params.get("provider_name", "").strip()

                if not provider_name:
                    return self.send_error_json("Provider name is required", 400)

                # Parse all files from multipart
                files, files_metadata = parse_multipart_files(body, content_type)

                if not files:
                    return self.send_error_json("No files uploaded", 400)

                if len(files) > MAX_FILES_PER_CONTRACT:
                    return self.send_error_json(f"Maximum {MAX_FILES_PER_CONTRACT} files allowed per contract", 400)

                # Parse JSON fields from query params
                key_terms = None
                if params.get("key_terms"):
                    try:
                        key_terms = json.loads(params["key_terms"])
                    except json.JSONDecodeError:
                        key_terms = None

                parties = None
                if params.get("parties"):
                    try:
                        parties = json.loads(params["parties"])
                    except json.JSONDecodeError:
                        parties = None

                risks = None
                if params.get("risks"):
                    try:
                        risks = json.loads(params["risks"])
                    except json.JSONDecodeError:
                        risks = None

                # Create contract record first (without file_path/file_name for multi-file)
                contract_data = {
                    "user_id": user_id,
                    "provider_name": provider_name,
                    "contract_nickname": params.get("contract_nickname"),
                    "contract_type": params.get("contract_type"),
                    "monthly_cost": float(params["monthly_cost"]) if params.get("monthly_cost") else None,
                    "annual_cost": float(params["annual_cost"]) if params.get("annual_cost") else None,
                    "currency": params.get("currency", "USD"),
                    "start_date": params.get("start_date"),
                    "end_date": params.get("end_date"),
                    "auto_renewal": params.get("auto_renewal", "true").lower() == "true",
                    "cancellation_notice_days": int(params["cancellation_notice_days"]) if params.get("cancellation_notice_days") else None,
                    "key_terms": key_terms,
                    "parties": parties,
                    "risks": risks,
                    "user_verified": True,
                }

                # For backward compatibility, set file_path and file_name from first file
                if files:
                    first_file = files[0]
                    contract_data["file_name"] = first_file["filename"]

                contract_data = {k: v for k, v in contract_data.items() if v is not None}

                result = supabase.table("contracts").insert(contract_data).execute()
                contract_id = result.data[0]["id"]

                # Upload each file to storage and create contract_files records
                for i, file_data in enumerate(files):
                    filename = file_data["filename"]
                    file_content = file_data["content"]

                    # Get metadata for this file
                    doc_type = "other"
                    label = filename
                    if files_metadata and i < len(files_metadata):
                        doc_type = files_metadata[i].get("document_type", "other")
                        label = files_metadata[i].get("label", filename)

                    # Storage path includes contract_id
                    file_path = f"{user_id}/{contract_id}/{filename}"

                    try:
                        supabase.storage.from_("contracts").upload(
                            file_path,
                            file_content,
                            {"content-type": "application/pdf"}
                        )
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            pass  # Ignore upload errors

                    # Create contract_files record
                    supabase.table("contract_files").insert({
                        "contract_id": contract_id,
                        "file_path": file_path,
                        "file_name": filename,
                        "file_size_bytes": len(file_content),
                        "document_type": doc_type,
                        "label": label,
                        "display_order": i
                    }).execute()

                # Also update the contract with the first file's path (for backward compatibility)
                if files:
                    first_file_path = f"{user_id}/{contract_id}/{files[0]['filename']}"
                    supabase.table("contracts").update({
                        "file_path": first_file_path
                    }).eq("id", contract_id).execute()

                # Return the created contract with files
                contract_result = supabase.table("contracts").select("*").eq("id", contract_id).single().execute()
                files_result = supabase.table("contract_files").select("*").eq("contract_id", contract_id).order("display_order").execute()
                contract_result.data["files"] = files_result.data

                return self.send_json(contract_result.data)

            except Exception as e:
                import traceback
                error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                return self.send_error_json(f"Failed to save contract: {error_details}", 500)

        # Generate recommendations using AI
        if path == "/api/recommendations/generate":
            try:
                import anthropic

                # Fetch all user's contracts
                contracts = supabase.table("contracts").select("*").eq("user_id", user_id).execute()

                if not contracts.data:
                    return self.send_json([])

                # Build context for Claude
                contracts_summary = []
                for c in contracts.data:
                    contracts_summary.append({
                        "id": c["id"],
                        "provider": c.get("provider_name"),
                        "type": c.get("contract_type"),
                        "monthly_cost": c.get("monthly_cost"),
                        "annual_cost": c.get("annual_cost"),
                        "start_date": c.get("start_date"),
                        "end_date": c.get("end_date"),
                        "auto_renewal": c.get("auto_renewal"),
                        "cancellation_notice_days": c.get("cancellation_notice_days"),
                        "key_terms": c.get("key_terms", []),
                        "risks": c.get("risks", []),
                    })

                prompt = f"""Analyze these contracts and provide actionable recommendations.

CONTRACTS:
{json.dumps(contracts_summary, indent=2)}

Generate recommendations in this JSON format. Each recommendation should reference a specific contract_id when applicable, or be null for portfolio-wide recommendations:

{{
    "recommendations": [
        {{
            "contract_id": "uuid or null for portfolio-wide",
            "type": "cost_reduction | consolidation | risk_alert | renewal_reminder",
            "title": "Short actionable title",
            "description": "Detailed explanation and action steps",
            "estimated_savings": number or null,
            "priority": "high | medium | low",
            "reasoning": "Why this recommendation matters"
        }}
    ]
}}

Focus on:
1. Cost reduction opportunities (negotiate, switch providers, remove unused services)
2. Consolidation (combine similar contracts for better rates)
3. Risk alerts (auto-renewals, unfavorable terms, missing cancellation windows)
4. Renewal reminders (contracts expiring soon that need attention)

Provide 3-7 specific, actionable recommendations. Return ONLY valid JSON."""

                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                response = client.messages.create(
                    model="claude-opus-4-5-20251101",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}]
                )

                result_text = response.content[0].text
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                ai_result = json.loads(result_text.strip())
                recommendations = ai_result.get("recommendations", [])

                # Clear old pending recommendations for this user
                supabase.table("recommendations").delete().eq("user_id", user_id).in_("status", ["pending", "viewed"]).execute()

                # Insert new recommendations
                inserted = []
                for rec in recommendations:
                    rec_data = {
                        "user_id": user_id,
                        "contract_id": rec.get("contract_id"),
                        "type": rec.get("type", "cost_reduction"),
                        "title": rec.get("title", "Recommendation"),
                        "description": rec.get("description", ""),
                        "estimated_savings": rec.get("estimated_savings"),
                        "priority": rec.get("priority", "medium"),
                        "status": "pending",
                        "reasoning": rec.get("reasoning"),
                    }
                    result = supabase.table("recommendations").insert(rec_data).execute()
                    if result.data:
                        inserted.append(result.data[0])

                return self.send_json(inserted)

            except Exception as e:
                import traceback
                error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                return self.send_error_json(f"Failed to generate recommendations: {error_details}", 500)

        return self.send_error_json("Not found", 404)

    def do_PUT(self):
        """Handle PUT requests."""
        path = urlparse(self.path).path

        token = parse_authorization(dict(self.headers))
        if not token:
            return self.send_error_json("No token provided", 401)

        try:
            user_id = get_user_from_token(token)
        except Exception as e:
            return self.send_error_json(f"Invalid token: {str(e)}", 401)

        supabase = get_supabase_client()

        # Update recommendation status
        if path.startswith("/api/recommendations/"):
            try:
                rec_id = path.split("/")[-1]

                # Read body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode()) if body else {}

                status = data.get("status")
                if status not in ["accepted", "dismissed"]:
                    return self.send_error_json("Invalid status", 400)

                # Verify ownership
                existing = supabase.table("recommendations").select("id").eq("id", rec_id).eq("user_id", user_id).single().execute()
                if not existing.data:
                    return self.send_error_json("Recommendation not found", 404)

                # Update status
                result = supabase.table("recommendations").update({
                    "status": status,
                    "acted_on_at": "now()"
                }).eq("id", rec_id).execute()

                return self.send_json(result.data[0] if result.data else {"status": "updated"})

            except Exception as e:
                import traceback
                error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                return self.send_error_json(f"Failed to update recommendation: {error_details}", 500)

        return self.send_error_json("Not found", 404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        path = urlparse(self.path).path

        token = parse_authorization(dict(self.headers))
        if not token:
            return self.send_error_json("No token provided", 401)

        try:
            user_id = get_user_from_token(token)
        except Exception as e:
            return self.send_error_json(f"Invalid token: {str(e)}", 401)

        supabase = get_supabase_client()

        if path.startswith("/api/contracts/"):
            contract_id = path.split("/")[-1]

            # Verify ownership and get contract
            existing = supabase.table("contracts").select("id").eq("id", contract_id).eq("user_id", user_id).single().execute()

            if not existing.data:
                return self.send_error_json("Contract not found", 404)

            # Get all files for this contract to delete from storage
            files = supabase.table("contract_files").select("file_path").eq("contract_id", contract_id).execute()

            # Delete files from storage
            for file in files.data:
                if file.get("file_path"):
                    try:
                        supabase.storage.from_("contracts").remove([file["file_path"]])
                    except:
                        pass

            # Also try to delete legacy file_path if exists
            contract = supabase.table("contracts").select("file_path").eq("id", contract_id).single().execute()
            if contract.data and contract.data.get("file_path"):
                try:
                    supabase.storage.from_("contracts").remove([contract.data["file_path"]])
                except:
                    pass

            # Delete contract (contract_files will be deleted via CASCADE)
            supabase.table("contracts").delete().eq("id", contract_id).execute()
            return self.send_json({"status": "deleted"})

        return self.send_error_json("Not found", 404)
