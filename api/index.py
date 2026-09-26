import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from api.auth import _handle_request as auth_request
from api.crawl import _handle_request as crawl_request
from api.advanced import _handle_request as advanced_request
from api.save_csv import _handle_request as save_request

ROUTES = {
    "/api/auth": auth_request,
    "/api/crawl": crawl_request,
    "/api/advanced": advanced_request,
    "/api/save_csv": save_request,
}

class handler(BaseHTTPRequestHandler):
    def _dispatch(self):
        qs = parse_qs(urlparse(self.path).query)
        forwarded = qs.get("path", [""])[0].strip("/")
        path = "/api/" + forwarded if forwarded else urlparse(self.path).path.rstrip("/") or "/"
        target = ROUTES.get(path)
        if target is None:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"Unknown API endpoint"}')
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        request = type("Request", (), {
            "method": self.command,
            "headers": self.headers,
            "body": body,
        })()
        result = target(request)

        self.send_response(result.get("statusCode", 500))
        for key, value in result.get("headers", {}).items():
            if value:
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(result.get("body", "").encode("utf-8"))

    def do_POST(self):
        self._dispatch()

    def do_GET(self):
        self._dispatch()
