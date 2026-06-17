from pathlib import Path
import json

root = Path(r"D:\PYTHON\Forge Francaise")
profiles_path = root / "backend" / "data" / "profiles.json"

if profiles_path.exists():
    payload = json.loads(profiles_path.read_text(encoding="utf-8-sig"))

    for profile in payload.get("profiles", []):
        if profile.get("id") == "local_lizard":
            profile["voice_id"] = "edge_fr_denise"

    profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("profile voice set to edge_fr_denise")
else:
    print("profiles.json not found yet, skipping")
