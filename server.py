#!/usr/bin/env python3
"""
Jira Daily Tracker - Local Proxy Server
Run: python server.py
Then open: http://localhost:8765/jira-daily-tracker.html
"""

import json
import base64
import urllib.request
import urllib.error
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8765

class ProxyHandler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        if args and '/jira-proxy' in str(args[0]):
            print(f"  → Jira API call: {args[1]}")
        else:
            super().log_message(format, *args)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/jira-proxy':
            self._handle_proxy()
        else:
            self.send_error(404)

    def _handle_proxy(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        payload = json.loads(body)

        jira_url = payload['jiraUrl'].rstrip('/')
        email    = payload['email']
        token    = payload['token']
        method   = payload.get('method', 'GET')
        endpoint = payload['endpoint']
        data     = payload.get('data')

        auth = base64.b64encode(f"{email}:{token}".encode()).decode()
        full_url = jira_url + endpoint

        # ── Attachment upload (multipart) ──────────────────
        if data and data.get('_attachment'):
            self._upload_attachment(full_url, auth, data)
            return

        # ── Regular JSON request ───────────────────────────
        req_body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            full_url,
            data=req_body,
            method=method,
            headers={
                'Authorization': f'Basic {auth}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )
        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp_body)
        except Exception as e:
            self._json_error(500, str(e))

    def _upload_attachment(self, full_url, auth, data):
        """Upload file as multipart/form-data to Jira attachment API."""
        try:
            file_bytes = base64.b64decode(data['base64'])
            filename   = data.get('name', 'attachment')
            mime_type  = data.get('mimeType', 'application/octet-stream')

            boundary = uuid.uuid4().hex
            body_parts = []
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
            body_parts.append(f'Content-Type: {mime_type}'.encode())
            body_parts.append(b'')
            body_parts.append(file_bytes)
            body_parts.append(f'--{boundary}--'.encode())
            req_body = b'\r\n'.join(body_parts)

            req = urllib.request.Request(
                full_url,
                data=req_body,
                method='POST',
                headers={
                    'Authorization': f'Basic {auth}',
                    'Accept': 'application/json',
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'X-Atlassian-Token': 'no-check',
                }
            )
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp_body)
        except Exception as e:
            self._json_error(500, str(e))

    def _json_error(self, code, msg):
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': msg}).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')


if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), ProxyHandler)
    print(f"\n  ✓ Jira Daily Tracker proxy running!")
    print(f"  → Open http://localhost:{PORT}/jira-daily-tracker.html\n")
    print(f"  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")