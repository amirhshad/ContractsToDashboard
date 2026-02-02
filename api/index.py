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


# Multi-document extraction prompt
MULTI_DOC_EXTRACTION_PROMPT = """You are analyzing a contract package consisting of one or more related documents.
These documents together form a single contractual relationship (e.g., a Framework Agreement with SOWs,
a Policy with Terms & Conditions, etc.).

Analyze ALL provided documents together and extract a UNIFIED view of the contract:

{
    "provider_name": "Company/service provider name (from main agreement)",
    "contract_type": "One of: insurance, utility, subscription, rental, saas, service, other",
    "monthly_cost": "Total monthly cost across all documents, as a number or null",
    "annual_cost": "Total annual cost across all documents, as a number or null",
    "start_date": "Earliest effective start date in YYYY-MM-DD format or null",
    "end_date": "Latest end date in YYYY-MM-DD format or null",
    "auto_renewal": true or false (from main agreement or as overridden by amendments),
    "cancellation_notice_days": "Number of days notice required or null",
    "key_terms": ["List of important terms from ALL documents"],
    "confidence": 0.0-1.0 confidence score,
    "documents_analyzed": [
        {
            "filename": "original filename",
            "document_type": "detected type: main_agreement, sow, terms_conditions, amendment, addendum, exhibit, schedule, or other",
            "summary": "Brief 1-sentence summary of what this document covers"
        }
    ]
}

IMPORTANT:
- If documents have conflicting terms, note the conflict in key_terms and use the most recent/specific version
- Amendments and SOWs typically override terms in the main agreement
- Combine costs if multiple SOWs/schedules specify separate fees
- Return ONLY the JSON object, no additional text."""


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
            return self.send_json({"status": "healthy", "service": "Contract Optimizer API"})

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
                    "text": MULTI_DOC_EXTRACTION_PROMPT
                })

                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    messages=[{
                        "role": "user",
                        "content": content
                    }]
                )

                result_text = response.content[0].text
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                extraction = json.loads(result_text.strip())

                # Add file names to extraction result
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

                # Parse key_terms from JSON string
                key_terms = None
                if params.get("key_terms"):
                    try:
                        key_terms = json.loads(params["key_terms"])
                    except json.JSONDecodeError:
                        key_terms = None

                # Create contract record first (without file_path/file_name for multi-file)
                contract_data = {
                    "user_id": user_id,
                    "provider_name": provider_name,
                    "contract_type": params.get("contract_type"),
                    "monthly_cost": float(params["monthly_cost"]) if params.get("monthly_cost") else None,
                    "annual_cost": float(params["annual_cost"]) if params.get("annual_cost") else None,
                    "start_date": params.get("start_date"),
                    "end_date": params.get("end_date"),
                    "auto_renewal": params.get("auto_renewal", "true").lower() == "true",
                    "cancellation_notice_days": int(params["cancellation_notice_days"]) if params.get("cancellation_notice_days") else None,
                    "key_terms": key_terms,
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
