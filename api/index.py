"""Vercel serverless API using basic HTTP handler."""

from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs
import base64

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


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
            return self.send_json(result.data)

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

        if path.startswith("/api/contracts/"):
            contract_id = path.split("/")[-1]
            result = supabase.table("contracts").select("*").eq("id", contract_id).eq("user_id", user_id).single().execute()
            if not result.data:
                return self.send_error_json("Contract not found", 404)
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

        # Upload extract
        if path == "/api/upload/extract":
            try:
                import anthropic
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                # Parse multipart form data (simplified)
                content_type = self.headers.get("Content-Type", "")
                if "multipart/form-data" in content_type:
                    boundary = content_type.split("boundary=")[1].encode()
                    parts = body.split(b"--" + boundary)
                    file_content = None
                    filename = None
                    
                    for part in parts:
                        if b"filename=" in part:
                            # Extract filename
                            header_end = part.find(b"\r\n\r\n")
                            header = part[:header_end].decode()
                            if 'filename="' in header:
                                filename = header.split('filename="')[1].split('"')[0]
                            file_content = part[header_end + 4:].rstrip(b"\r\n--")
                            break

                    if not file_content:
                        return self.send_error_json("No file uploaded", 400)

                    base64_content = base64.standard_b64encode(file_content).decode("utf-8")

                    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

                    extraction_prompt = """Analyze this contract document and extract the following information in JSON format:
{
    "provider_name": "Company/service provider name",
    "contract_type": "One of: insurance, utility, subscription, rental, saas, service, other",
    "monthly_cost": "Monthly cost as a number or null",
    "annual_cost": "Annual cost as a number or null",
    "start_date": "Start date in YYYY-MM-DD format or null",
    "end_date": "End date in YYYY-MM-DD format or null",
    "auto_renewal": true/false,
    "cancellation_notice_days": "Number of days notice required or null",
    "key_terms": ["List of important terms or conditions"],
    "confidence": 0.0-1.0 confidence score
}
Return ONLY the JSON object, no additional text."""

                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": base64_content}},
                                {"type": "text", "text": extraction_prompt}
                            ]
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
                    extraction["file_name"] = filename
                    return self.send_json(extraction)

            except Exception as e:
                return self.send_error_json(f"Extraction failed: {str(e)}", 500)

        # Upload confirm
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

                # Parse multipart for file
                if "multipart/form-data" in content_type:
                    boundary = content_type.split("boundary=")[1].encode()
                    parts = body.split(b"--" + boundary)
                    file_content = None
                    filename = None

                    for part in parts:
                        if b"filename=" in part:
                            header_end = part.find(b"\r\n\r\n")
                            header = part[:header_end].decode()
                            if 'filename="' in header:
                                filename = header.split('filename="')[1].split('"')[0]
                            file_content = part[header_end + 4:].rstrip(b"\r\n--")
                            break

                    if file_content and filename:
                        file_path = f"{user_id}/{filename}"
                        try:
                            supabase.storage.from_("contracts").upload(file_path, file_content, {"content-type": "application/pdf"})
                        except Exception as e:
                            if "already exists" not in str(e).lower():
                                pass  # Ignore upload errors

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
                            "file_path": file_path,
                            "file_name": filename,
                            "user_verified": True,
                        }
                        contract_data = {k: v for k, v in contract_data.items() if v is not None}

                        result = supabase.table("contracts").insert(contract_data).execute()
                        return self.send_json(result.data[0])

                return self.send_error_json("No file uploaded", 400)

            except Exception as e:
                return self.send_error_json(f"Failed to save contract: {str(e)}", 500)

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
            existing = supabase.table("contracts").select("id, file_path").eq("id", contract_id).eq("user_id", user_id).single().execute()

            if not existing.data:
                return self.send_error_json("Contract not found", 404)

            if existing.data.get("file_path"):
                try:
                    supabase.storage.from_("contracts").remove([existing.data["file_path"]])
                except:
                    pass

            supabase.table("contracts").delete().eq("id", contract_id).execute()
            return self.send_json({"status": "deleted"})

        return self.send_error_json("Not found", 404)
