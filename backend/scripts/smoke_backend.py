import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

checks = [
    ("GET", "/api/health", None),
    ("GET", "/api/settings", None),
    ("GET", "/api/diagnostics", None),
    ("GET", "/api/app/bootstrap", None),
    ("GET", "/api/course", None),
    ("GET", "/api/course/sections/start", None),
    ("GET", "/api/lessons/greetings_001", None),
    ("GET", "/api/codex", None),
    ("GET", "/api/vulgar/items", None),
    ("GET", "/api/review/local_lizard/session?mode=quick&limit=3", None),
    ("GET", "/api/progress/local_lizard/summary", None),
    ("GET", "/api/audio/voices", None),
    (
        "POST",
        "/api/practice/answer",
        {
            "profile_id": "local_lizard",
            "lesson_id": "greetings_001",
            "exercise_id": "ex_bonjour_translation",
            "answer": "здравствуйте",
        },
    ),
    (
        "POST",
        "/api/audio/speak",
        {
            "text": "Bonjour, monsieur.",
            "lang": "fr",
            "voice_id": "mock_fr_female",
            "speed": 1,
            "mode": "normal",
        },
    ),
]

failures = []

for method, path, payload in checks:
    if method == "GET":
        response = client.get(path)
    elif method == "POST":
        response = client.post(path, json=payload)
    else:
        raise RuntimeError(f"Unsupported method: {method}")

    ok = 200 <= response.status_code < 300
    print(f"{method} {path} -> {response.status_code}")

    if not ok:
        failures.append({
            "method": method,
            "path": path,
            "status": response.status_code,
            "body": response.text[:500],
        })

if failures:
    print("")
    print("SMOKE FAILED")
    print(json.dumps(failures, ensure_ascii=False, indent=2))
    raise SystemExit(1)

print("")
print("SMOKE PASSED")
