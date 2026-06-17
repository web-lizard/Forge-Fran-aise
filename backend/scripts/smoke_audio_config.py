import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

errors = []

profiles_path = ROOT / "data" / "profiles.json"

if profiles_path.exists():
    payload = json.loads(profiles_path.read_text(encoding="utf-8-sig"))
    profiles = payload.get("profiles", [])
    local = next((item for item in profiles if item.get("id") == "local_lizard"), None)

    if not local:
        errors.append("local_lizard profile is missing")
    elif str(local.get("voice_id", "")).startswith("mock_"):
        errors.append("local_lizard voice_id still points to mock voice")
else:
    errors.append("profiles.json is missing")

voices_response = client.get("/api/audio/voices")
if voices_response.status_code != 200:
    errors.append(f"/api/audio/voices failed: {voices_response.status_code}")
else:
    voices = voices_response.json()
    edge_voices = [voice for voice in voices if voice.get("engine") == "edge"]

    if not edge_voices:
        errors.append("No edge voices exposed by /api/audio/voices")

mock_response = client.post(
    "/api/audio/speak",
    json={
        "text": "Bonjour, monsieur.",
        "lang": "fr",
        "voice_id": "mock_fr_female",
        "speed": 1,
        "mode": "normal",
    },
)

if mock_response.status_code != 200:
    errors.append(f"mock /api/audio/speak failed: {mock_response.status_code}")
else:
    body = mock_response.json()
    if body.get("provider") != "mock":
        errors.append(f"mock /api/audio/speak returned unexpected provider: {body.get('provider')}")

if errors:
    print("AUDIO CONFIG SMOKE FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("AUDIO CONFIG SMOKE PASSED")
