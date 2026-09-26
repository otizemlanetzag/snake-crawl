import json
import os
from .security import session_cookie
from pathlib import Path

def _secret():
    # Prefer Vercel environment variable in production.
    env = os.environ.get("SNAKE_CRAWL_SECRET")
    if env:
        return env.strip()
    p = Path(__file__).resolve().parent.parent / "SECRET_CODE"
    try:
        return p.read_text(encoding="utf-8").strip()
    except Exception:
        return ""

def main(request):
    if request.method != "POST":
        return {"statusCode":405,"headers":{"Content-Type":"application/json"},"body":json.dumps({"error":"POST only"})}
    try:
        body = request.body if isinstance(request.body, dict) else json.loads(request.body or "{}")
        supplied = str(body.get("code","")).strip()
        secret = _secret()
        ok = bool(secret) and supplied == secret and secret != "CHANGE_THIS_SECRET_CODE"
        return {
            "statusCode":200 if ok else 401,
            "headers":{"Content-Type":"application/json","Cache-Control":"no-store","Set-Cookie":session_cookie() if ok else ""},
            "body":json.dumps({"authenticated":ok})
        }
    except Exception:
        return {"statusCode":400,"headers":{"Content-Type":"application/json"},"body":json.dumps({"authenticated":False})}
