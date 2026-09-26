from api.security import valid_session
from Advanced_crawl.advanced_crawl import handler

def _handle_request(request):
    if not valid_session(request):
        return {"statusCode":401,"headers":{"Content-Type":"application/json","Cache-Control":"no-store"},"body":"{\"error\":\"Authentication required\"}"}
    return handler(request)

from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        request = type("Request", (), {"method":"POST", "headers":self.headers, "body":body})()
        result = _handle_request(request)
        self.send_response(result.get("statusCode", 500))
        for key, value in result.get("headers", {}).items():
            if value:
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(result.get("body", "").encode("utf-8"))

    def do_GET(self):
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"POST only"}')
