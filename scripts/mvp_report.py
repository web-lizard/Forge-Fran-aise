import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "content"
REPORTS_ROOT = ROOT / "reports"
REPORTS_ROOT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def cmd(command: list[str]) -> str:
    result = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True, check=False)
    return (result.stdout or result.stderr or "").strip()

sections = []
lessons = []
exercises = []
vulgar_items = []
codex_entries = []

for section_path in sorted((CONTENT_ROOT / "sections").glob("*/section.json")):
    section = read_json(section_path)
    sections.append(section)

for lesson_path in sorted((CONTENT_ROOT / "sections").glob("*/lessons/*.json")):
    lesson = read_json(lesson_path)
    lessons.append(lesson)
    exercises.extend(lesson.get("exercises", []))

for pack_path in sorted((CONTENT_ROOT / "vulgar" / "packs").glob("*.json")):
    pack = read_json(pack_path)
    vulgar_items.extend(pack.get("items", []))

for codex_path in sorted((CONTENT_ROOT / "codex").glob("*.json")):
    codex_entries.append(read_json(codex_path))

git_commit = cmd(["git", "rev-parse", "--short", "HEAD"])
git_status = cmd(["git", "status", "--short"])

lines = []
lines.append("# Forge Française MVP Report")
lines.append("")
lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
lines.append("")
lines.append("## Status")
lines.append("")
lines.append("- Version: 0.6.0")
lines.append("- Backend: http://127.0.0.1:8797/api/health")
lines.append("- Frontend: http://127.0.0.1:5197")
lines.append(f"- Git commit: {git_commit or 'unknown'}")
lines.append(f"- Git dirty: {'yes' if git_status else 'no'}")
lines.append("")
lines.append("## Content")
lines.append("")
lines.append(f"- Sections: {len(sections)}")
lines.append(f"- Lessons: {len(lessons)}")
lines.append(f"- Exercises: {len(exercises)}")
lines.append(f"- Codex entries: {len(codex_entries)}")
lines.append(f"- Vulgar items: {len(vulgar_items)}")
lines.append("")
lines.append("## Sections")
lines.append("")

for section in sorted(sections, key=lambda item: item.get("order", 999)):
    lines.append(f"- {section['id']}: {section['title']['ru']} / {section['title']['fr']}")

lines.append("")
lines.append("## MVP Features")
lines.append("")
features = [
    "Vue 3 + TypeScript + Vite frontend",
    "FastAPI backend",
    "JSON content engine",
    "content validation",
    "mobile-first UI",
    "bottom navigation",
    "one-card lesson flow",
    "practice modes",
    "progress scoring",
    "weak topic review",
    "audio drill",
    "Edge TTS provider with mock fallback",
    "audio cache API",
    "RU / FR interface switch",
    "voice selector",
    "vulgar French library",
    "diagnostics endpoint",
    "smoke tests",
    "build scripts",
]

for feature in features:
    lines.append(f"- {feature}")

lines.append("")
lines.append("## Demo Flow")
lines.append("")
lines.append("1. Open http://127.0.0.1:5197")
lines.append("2. Continue the first lesson.")
lines.append("3. Open drill and answer several questions.")
lines.append("4. Open audio drill and test Edge voice.")
lines.append("5. Open profile and switch voice / language.")
lines.append("6. Open diagnostics.")
lines.append("")
lines.append("## Check Commands")
lines.append("")
lines.append("```cmd")
lines.append("scripts\\check_backend.cmd")
lines.append("scripts\\check_frontend.cmd")
lines.append("scripts\\check_all.cmd")
lines.append("```")
lines.append("")

report_path = REPORTS_ROOT / "MVP_REPORT.md"
report_path.write_text("\n".join(lines), encoding="utf-8")

print(f"Report written: {report_path}")
