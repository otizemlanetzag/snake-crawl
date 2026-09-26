"""Advanced discovery crawler for Snake Crawl.

Designed for Vercel/serverless use: one request performs a bounded batch of
random domain candidates. The web UI calls this endpoint repeatedly.
"""

import csv
import io
import json
import random
import string
import urllib.parse
import urllib.request

DEFAULT_MAX_SITES = 100
MAX_BATCH = 10
DEFAULT_MAX_LABEL_LENGTH = 20
REQUEST_TIMEOUT = 5

KEYS = string.ascii_lowercase + string.digits + "-"


def _iana_tlds():
    request = urllib.request.Request(
        "https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
        headers={"User-Agent": "Snake-Crawl/1.0"},
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        text = response.read().decode("utf-8", errors="replace")

    return [
        line.strip().lower()
        for line in text.splitlines()
        if line.strip() and not line.startswith("#")
    ]


def make_candidate(tlds, max_characters=DEFAULT_MAX_LABEL_LENGTH):
    length = random.randint(1, max(1, min(max_characters, 20)))
    label = "".join(random.choice(KEYS) for _ in range(length)).strip("-")
    if not label:
        label = random.choice(string.ascii_lowercase)
    return "https://" + label + "." + random.choice(tlds)


def fetch_candidate(url):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Snake-Crawl/1.0 (+bounded discovery)",
                "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
            },
        )
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            status = getattr(response, "status", 200)
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
            body = response.read(1_000_000)
            text = body.decode("utf-8", errors="replace")

        if "html" not in content_type.lower():
            clean_text = text[:100_000]
        else:
            # Small stdlib HTML text extraction; no third-party dependency.
            import re
            clean_text = re.sub(r"<script[\\s\\S]*?</script>", " ", text, flags=re.I)
            clean_text = re.sub(r"<style[\\s\\S]*?</style>", " ", clean_text, flags=re.I)
            clean_text = re.sub(r"<[^>]+>", " ", clean_text)
            clean_text = re.sub(r"\\s+", " ", clean_text).strip()[:100_000]

        return {
            "url": url,
            "final_url": final_url,
            "status": status,
            "content_type": content_type,
            "content": clean_text,
        }
    except Exception as exc:
        return {"url": url, "status": "error", "error": str(exc)}


def handler(request):
    if request.method != "POST":
        return _response({"error": "POST required"}, 405)

    try:
        payload = request.body() if hasattr(request, "body") else {}
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        if isinstance(payload, str):
            payload = json.loads(payload or "{}")
        payload = payload or {}

        requested = int(payload.get("count", 5))
        count = max(1, min(MAX_BATCH, requested))
        max_length = max(1, min(20, int(payload.get("max_characters", 20))))

        tlds = _iana_tlds()
        results = []
        seen = set()

        for _ in range(count):
            url = make_candidate(tlds, max_length)
            while url in seen:
                url = make_candidate(tlds, max_length)
            seen.add(url)
            results.append(fetch_candidate(url))

        return _response({
            "results": results,
            "tested": len(results),
            "found": sum(1 for item in results if item.get("status") == 200),
        })
    except Exception as exc:
        return _response({"error": str(exc)}, 500)


def _response(data, status=200):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(data, ensure_ascii=False),
    }


def write_csv(rows, path="DATA.CSV"):
    fields = ["url", "final_url", "status", "content_type", "content"]
    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


if __name__ == "__main__":
    print("This module is intended to be called through the Vercel API.")
