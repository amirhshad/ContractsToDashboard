"""Vercel serverless function entry point for FastAPI backend."""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = {"status": "ok", "message": "API is working", "path": self.path}
        self.wfile.write(json.dumps(message).encode())
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = {"status": "ok", "message": "POST received", "path": self.path}
        self.wfile.write(json.dumps(message).encode())
        return
