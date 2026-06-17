import json
import sys
import urllib.error
import urllib.request

API_BASE = "http://127.0.0.1:8797/api"

checks = [
    ("GET", "/health", None),
    ("GET", "/settings", None),
    ("GET", "/diagnostics", None),
    ("GET", "/app/bootstrap", None),
    ("GET", "/course", None),
    ("GET", "/audio/voices", None),
    ("POST", "/audio/speak", {
        "text": "Bonjour, monsieur.",
        "lang": "fr",
        "voice_id": "mock_fr_female",
        "speed": 1,
        "mode": "normal",
    }),
]

failures = []

def request(method: str, path: str, payload=None):
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(API_BASE + path, data=data, method=method, headers=headers)

    with urllib.request.urlopen(req, timeout=10) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, body

for method, path, payload in checks:
    try:
        status, body = request(method, path, payload)
        print(f"{method} {path} -> {status}")
        if not (200 <= status < 300):
            failures.append({"method": method, "path": path, "status": status, "body": body[:300]})
    except urllib.error.URLError as exc:
        print(f"{method} {path} -> ERROR {exc}")
        failures.append({"method": method, "path": path, "error": str(exc)})

if failures:
    print("")
    print("LIVE SMOKE FAILED")
    print(json.dumps(failures, ensure_ascii=False, indent=2))
    raise SystemExit(1)

print("")
print("LIVE SMOKE PASSED")
