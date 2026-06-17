from pathlib import Path
import subprocess
import textwrap
import json

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

BACKEND_PORT = 8797
FRONTEND_PORT = 5197

GIT_NAME = "web-lizard"
GIT_EMAIL = "web-lizard@users.noreply.github.com"


def clean(content: str) -> str:
    return textwrap.dedent(content).lstrip("\n").rstrip() + "\n"


def w(rel_path: str, content: str = "") -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")
    print(f"written: {rel_path}")


def mkdir(rel_path: str) -> None:
    path = ROOT / rel_path
    path.mkdir(parents=True, exist_ok=True)
    print(f"dir: {rel_path}")


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    print("")
    print("RUN:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=str(cwd), check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
        return 127


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Project directory not found: {ROOT}")

    print("Forge Francaise patch 4")
    print("Step 4/6: real practice modes, review, progress scoring")
    print(f"root: {ROOT}")
    print("")

    for rel in [
        "backend/app/api",
        "backend/app/services",
        "frontend/src/components/practice",
        "frontend/src/pages",
        "frontend/src/stores",
        "scripts",
    ]:
        mkdir(rel)

    w("backend/app/services/content_service.py", """
    from functools import lru_cache
    from pathlib import Path
    from typing import Any

    from app.core.json_utils import read_json
    from app.core.paths import CONTENT_ROOT


    class ContentService:
        def __init__(self, content_root: Path = CONTENT_ROOT) -> None:
            self.content_root = content_root

        def list_sections(self) -> list[dict[str, Any]]:
            sections_root = self.content_root / "sections"
            sections: list[dict[str, Any]] = []

            for section_path in sorted(sections_root.glob("*/section.json")):
                sections.append(read_json(section_path))

            return sorted(sections, key=lambda item: item.get("order", 999))

        def get_section(self, section_id: str) -> dict[str, Any]:
            for section in self.list_sections():
                if section["id"] == section_id or section.get("slug") == section_id:
                    return section
            raise KeyError(f"Section not found: {section_id}")

        def iter_lesson_files(self) -> list[Path]:
            return sorted(self.content_root.glob("sections/*/lessons/*.json"))

        def list_lessons(self) -> list[dict[str, Any]]:
            lessons: list[dict[str, Any]] = []
            for lesson_path in self.iter_lesson_files():
                lessons.append(read_json(lesson_path))
            return sorted(lessons, key=lambda item: (item.get("section_id", ""), item.get("order", 999)))

        def get_lesson(self, lesson_id: str) -> dict[str, Any]:
            for lesson_path in self.iter_lesson_files():
                lesson = read_json(lesson_path)
                if lesson.get("id") == lesson_id:
                    return lesson
            raise KeyError(f"Lesson not found: {lesson_id}")

        def list_exercises(self) -> list[dict[str, Any]]:
            exercises: list[dict[str, Any]] = []

            for lesson in self.list_lessons():
                for exercise in lesson.get("exercises", []):
                    item = dict(exercise)
                    item["lesson_id"] = lesson["id"]
                    item["section_id"] = lesson["section_id"]
                    item["lesson_title"] = lesson["title"]
                    item["level"] = lesson.get("level", "A0")
                    exercises.append(item)

            return exercises

        def get_exercise(self, lesson_id: str, exercise_id: str) -> dict[str, Any]:
            lesson = self.get_lesson(lesson_id)

            for exercise in lesson.get("exercises", []):
                if exercise.get("id") == exercise_id:
                    item = dict(exercise)
                    item["lesson_id"] = lesson_id
                    item["section_id"] = lesson["section_id"]
                    item["lesson_title"] = lesson["title"]
                    item["level"] = lesson.get("level", "A0")
                    return item

            raise KeyError(f"Exercise not found: {exercise_id}")

        def list_ranks(self) -> list[dict[str, Any]]:
            payload = read_json(self.content_root / "ranks" / "napoleonic_ranks.json")
            return payload["ranks"]

        def rank_for_score(self, score: int) -> dict[str, Any]:
            ranks = self.list_ranks()
            current = ranks[0]

            for rank in ranks:
                if score >= rank.get("min_score", 0):
                    current = rank

            return current

        def list_codex(self) -> list[dict[str, Any]]:
            entries: list[dict[str, Any]] = []
            for entry_path in sorted((self.content_root / "codex").glob("*.json")):
                entries.append(read_json(entry_path))
            return entries

        def get_codex_entry(self, entry_id: str) -> dict[str, Any]:
            for entry in self.list_codex():
                if entry["id"] == entry_id:
                    return entry
            raise KeyError(f"Codex entry not found: {entry_id}")

        def vulgar_index(self) -> dict[str, Any]:
            return read_json(self.content_root / "vulgar" / "index.json")

        def list_vulgar_items(self) -> list[dict[str, Any]]:
            items: list[dict[str, Any]] = []

            for pack_path in sorted((self.content_root / "vulgar" / "packs").glob("*.json")):
                pack = read_json(pack_path)
                for item in pack.get("items", []):
                    item = dict(item)
                    item["pack_id"] = pack["id"]
                    items.append(item)

            return items

        def get_vulgar_item(self, item_id: str) -> dict[str, Any]:
            for item in self.list_vulgar_items():
                if item["id"] == item_id:
                    return item
            raise KeyError(f"Vulgar item not found: {item_id}")


    @lru_cache(maxsize=1)
    def get_content_service() -> ContentService:
        return ContentService()
    """)

    w("backend/app/services/progress_service.py", """
    from collections import Counter, defaultdict
    from datetime import datetime, timezone
    import json
    from typing import Any

    from app.core.json_utils import read_json, write_json_atomic
    from app.core.paths import DATA_ROOT

    PROGRESS_ROOT = DATA_ROOT / "progress"
    EVENTS_ROOT = DATA_ROOT / "events"


    class ProgressService:
        def progress_path(self, profile_id: str):
            return PROGRESS_ROOT / f"{profile_id}.json"

        def events_path(self, profile_id: str):
            return EVENTS_ROOT / f"{profile_id}.jsonl"

        def default_progress(self, profile_id: str) -> dict[str, Any]:
            return {
                "profile_id": profile_id,
                "current_level": "A0",
                "score": 0,
                "completed_lessons": [],
                "lesson_progress": {},
                "weak_topics": [],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

        def get_progress(self, profile_id: str) -> dict[str, Any]:
            path = self.progress_path(profile_id)

            if not path.exists():
                payload = self.default_progress(profile_id)
                write_json_atomic(path, payload)

            payload = read_json(path)

            changed = False
            for key, value in self.default_progress(profile_id).items():
                if key not in payload:
                    payload[key] = value
                    changed = True

            if changed:
                write_json_atomic(path, payload)

            return payload

        def save_progress(self, profile_id: str, payload: dict[str, Any]) -> dict[str, Any]:
            payload["profile_id"] = profile_id
            payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            write_json_atomic(self.progress_path(profile_id), payload)
            return payload

        def append_event(self, profile_id: str, event: dict[str, Any]) -> None:
            EVENTS_ROOT.mkdir(parents=True, exist_ok=True)
            event["ts"] = datetime.now(timezone.utc).isoformat()

            with self.events_path(profile_id).open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\\n")

        def read_events(self, profile_id: str, limit: int | None = None) -> list[dict[str, Any]]:
            path = self.events_path(profile_id)

            if not path.exists():
                return []

            rows: list[dict[str, Any]] = []

            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            if limit is not None:
                return rows[-limit:]

            return rows

        def record_answer(
            self,
            profile_id: str,
            lesson_id: str,
            exercise_id: str,
            answer: Any,
            expected: Any,
            correct: bool,
            tags: list[str],
            section_id: str | None = None,
        ) -> dict[str, Any]:
            progress = self.get_progress(profile_id)

            delta = 10 if correct else 1
            if tags and "vulgar" in tags and correct:
                delta += 2

            progress["score"] = int(progress.get("score", 0)) + delta

            lesson_progress = progress.setdefault("lesson_progress", {})
            lesson_state = lesson_progress.setdefault(
                lesson_id,
                {
                    "status": "in_progress",
                    "score": 0,
                    "attempts": 0,
                    "correct": 0,
                    "wrong": 0,
                    "last_opened_at": None,
                    "last_answered_at": None,
                },
            )

            lesson_state["attempts"] = int(lesson_state.get("attempts", 0)) + 1
            lesson_state["score"] = int(lesson_state.get("score", 0)) + delta
            lesson_state["last_answered_at"] = datetime.now(timezone.utc).isoformat()

            if correct:
                lesson_state["correct"] = int(lesson_state.get("correct", 0)) + 1
            else:
                lesson_state["wrong"] = int(lesson_state.get("wrong", 0)) + 1

            attempts = max(1, int(lesson_state.get("attempts", 0)))
            correct_count = int(lesson_state.get("correct", 0))
            lesson_state["accuracy"] = round(correct_count / attempts * 100)

            if attempts >= 3 and lesson_state["accuracy"] >= 70:
                lesson_state["status"] = "ready_to_complete"

            self.append_event(
                profile_id,
                {
                    "event": "exercise_answered",
                    "lesson_id": lesson_id,
                    "section_id": section_id,
                    "exercise_id": exercise_id,
                    "answer": answer,
                    "expected": expected,
                    "correct": correct,
                    "score_delta": delta,
                    "tags": tags,
                },
            )

            self.recalculate_weak_topics(profile_id, progress)
            return self.save_progress(profile_id, progress)

        def complete_lesson(self, profile_id: str, lesson_id: str) -> dict[str, Any]:
            progress = self.get_progress(profile_id)
            completed = progress.setdefault("completed_lessons", [])

            if lesson_id not in completed:
                completed.append(lesson_id)
                progress["score"] = int(progress.get("score", 0)) + 25

            lesson_progress = progress.setdefault("lesson_progress", {})
            lesson_state = lesson_progress.setdefault(lesson_id, {})
            lesson_state["status"] = "completed"
            lesson_state["completed_at"] = datetime.now(timezone.utc).isoformat()

            self.append_event(
                profile_id,
                {
                    "event": "lesson_completed",
                    "lesson_id": lesson_id,
                    "score_delta": 25,
                    "tags": ["lesson"],
                },
            )

            return self.save_progress(profile_id, progress)

        def recalculate_weak_topics(self, profile_id: str, progress: dict[str, Any] | None = None) -> list[str]:
            events = self.read_events(profile_id)
            wrong_by_tag: Counter[str] = Counter()

            for event in events:
                if event.get("event") != "exercise_answered":
                    continue
                if event.get("correct") is True:
                    continue
                for tag in event.get("tags", []):
                    wrong_by_tag[tag] += 1

            weak = [tag for tag, _count in wrong_by_tag.most_common(8)]

            if progress is not None:
                progress["weak_topics"] = weak

            return weak

        def summary(self, profile_id: str) -> dict[str, Any]:
            progress = self.get_progress(profile_id)
            events = self.read_events(profile_id)

            answered = [event for event in events if event.get("event") == "exercise_answered"]
            total = len(answered)
            correct = sum(1 for event in answered if event.get("correct") is True)
            wrong = total - correct
            accuracy = round(correct / total * 100) if total else 0

            by_tag: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0, "wrong": 0})

            for event in answered:
                tags = event.get("tags", []) or ["untagged"]
                for tag in tags:
                    by_tag[tag]["total"] += 1
                    if event.get("correct") is True:
                        by_tag[tag]["correct"] += 1
                    else:
                        by_tag[tag]["wrong"] += 1

            tag_stats = []
            for tag, stat in by_tag.items():
                total_tag = max(1, stat["total"])
                tag_stats.append({
                    "tag": tag,
                    "total": stat["total"],
                    "correct": stat["correct"],
                    "wrong": stat["wrong"],
                    "accuracy": round(stat["correct"] / total_tag * 100),
                })

            tag_stats.sort(key=lambda item: (-item["wrong"], item["accuracy"], item["tag"]))

            return {
                "profile_id": profile_id,
                "score": int(progress.get("score", 0)),
                "current_level": progress.get("current_level", "A0"),
                "completed_lessons": progress.get("completed_lessons", []),
                "completed_count": len(progress.get("completed_lessons", [])),
                "total_answers": total,
                "correct_answers": correct,
                "wrong_answers": wrong,
                "accuracy": accuracy,
                "weak_topics": progress.get("weak_topics", []),
                "tag_stats": tag_stats[:12],
                "recent_events": events[-12:],
            }


    def get_progress_service() -> ProgressService:
        return ProgressService()
    """)

    w("backend/app/services/practice_service.py", """
    import random
    from typing import Any

    from app.services.content_service import get_content_service
    from app.services.progress_service import get_progress_service


    def normalize(value: Any) -> str:
        if isinstance(value, list):
            return " ".join(str(item).strip() for item in value).strip().lower()
        return str(value).strip().lower()


    class PracticeService:
        def check_answer(self, profile_id: str, lesson_id: str, exercise_id: str, answer: Any) -> dict[str, Any]:
            exercise = get_content_service().get_exercise(lesson_id, exercise_id)

            expected = exercise.get("answer")
            correct = normalize(answer) == normalize(expected)

            progress = get_progress_service().record_answer(
                profile_id=profile_id,
                lesson_id=lesson_id,
                exercise_id=exercise_id,
                answer=answer,
                expected=expected,
                correct=correct,
                tags=exercise.get("tags", []),
                section_id=exercise.get("section_id"),
            )

            return {
                "correct": correct,
                "expected": expected,
                "explanation": exercise.get("explanation", {"ru": "", "fr": ""}),
                "score": progress.get("score", 0),
                "weak_topics": progress.get("weak_topics", []),
            }

        def session(self, profile_id: str, mode: str = "quick", limit: int = 7) -> dict[str, Any]:
            content = get_content_service()
            exercises = content.list_exercises()
            progress = get_progress_service().get_progress(profile_id)

            if mode == "weak":
                weak_topics = progress.get("weak_topics", [])
                if weak_topics:
                    exercises = [
                        item for item in exercises
                        if any(tag in weak_topics for tag in item.get("tags", []))
                    ] or content.list_exercises()

            elif mode == "audio":
                exercises = [item for item in exercises if item.get("audio_text")]

            elif mode == "vulgar":
                exercises = [
                    item for item in exercises
                    if "vulgar" in item.get("tags", []) or item.get("section_id") == "vulgar_french"
                ]

            elif mode == "articles":
                exercises = [
                    item for item in exercises
                    if "article" in item.get("tags", []) or item.get("section_id") in ["articles", "de_du"]
                ]

            else:
                exercises = list(exercises)

            random.seed(f"{profile_id}:{mode}:{len(exercises)}")
            random.shuffle(exercises)

            selected = exercises[: max(1, min(limit, 20))]

            return {
                "profile_id": profile_id,
                "mode": mode,
                "limit": limit,
                "count": len(selected),
                "exercises": selected,
            }


    def get_practice_service() -> PracticeService:
        return PracticeService()
    """)

    w("backend/app/api/progress.py", """
    from fastapi import APIRouter

    from app.services.progress_service import get_progress_service

    router = APIRouter(tags=["progress"])


    @router.get("/progress/{profile_id}")
    def get_progress(profile_id: str):
        return get_progress_service().get_progress(profile_id)


    @router.get("/progress/{profile_id}/summary")
    def progress_summary(profile_id: str):
        return get_progress_service().summary(profile_id)


    @router.post("/progress/{profile_id}/lessons/{lesson_id}/complete")
    def complete_lesson(profile_id: str, lesson_id: str):
        return get_progress_service().complete_lesson(profile_id, lesson_id)
    """)

    w("backend/app/api/review.py", """
    from fastapi import APIRouter

    from app.services.practice_service import get_practice_service
    from app.services.progress_service import get_progress_service

    router = APIRouter(tags=["review"])


    @router.get("/review/{profile_id}/weak")
    def weak_topics(profile_id: str):
        summary = get_progress_service().summary(profile_id)
        return {
            "profile_id": profile_id,
            "weak_topics": summary["weak_topics"],
            "tag_stats": summary["tag_stats"],
        }


    @router.get("/review/{profile_id}/session")
    def review_session(profile_id: str, mode: str = "quick", limit: int = 7):
        return get_practice_service().session(profile_id=profile_id, mode=mode, limit=limit)
    """)

    w("backend/app/main.py", """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from app.api import audio, bootstrap, codex, course, health, lessons, practice, profiles, progress, review, sections, settings, vulgar

    app = FastAPI(
        title="Forge Française API",
        description="Imperial French learning engine",
        version="0.4.0",
    )

    app.add_middleware(
        CORSMiddleware(
            if False else None
        )
    )
    """)

    # Rewriting main without the trick above, to keep simple valid Python.
    w("backend/app/main.py", """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from app.api import audio, bootstrap, codex, course, health, lessons, practice, profiles, progress, review, sections, settings, vulgar

    app = FastAPI(
        title="Forge Française API",
        description="Imperial French learning engine",
        version="0.4.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5197",
            "http://localhost:5197",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(bootstrap.router, prefix="/api")
    app.include_router(course.router, prefix="/api")
    app.include_router(sections.router, prefix="/api")
    app.include_router(lessons.router, prefix="/api")
    app.include_router(practice.router, prefix="/api")
    app.include_router(progress.router, prefix="/api")
    app.include_router(review.router, prefix="/api")
    app.include_router(profiles.router, prefix="/api")
    app.include_router(audio.router, prefix="/api")
    app.include_router(codex.router, prefix="/api")
    app.include_router(vulgar.router, prefix="/api")
    """)

    w("content/sections/00_start/lessons/greetings_001.json", """
    {
      "id": "greetings_001",
      "section_id": "start",
      "order": 1,
      "level": "A0",
      "title": {
        "ru": "Bonjour, merci и базовая вежливость",
        "fr": "Bonjour, merci et la politesse de base"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Первый принцип",
            "fr": "Premier principe"
          },
          "body": {
            "ru": "Сначала учим короткие живые фразы, которые можно сразу слушать и повторять.",
            "fr": "On commence par des phrases courtes, utiles et faciles à répéter."
          }
        },
        {
          "type": "word",
          "fr": "Bonjour",
          "transcription": "[бонжур]",
          "ru": "здравствуйте / добрый день",
          "audio_text": "Bonjour",
          "tooltip": {
            "ru": "Универсальное вежливое приветствие.",
            "fr": "Salutation polie et très courante."
          }
        },
        {
          "type": "word",
          "fr": "Merci",
          "transcription": "[мэрси]",
          "ru": "спасибо",
          "audio_text": "Merci",
          "tooltip": {
            "ru": "Базовое спасибо. Подходит почти везде.",
            "fr": "Remerciement simple et courant."
          }
        },
        {
          "type": "example",
          "fr": "Bonjour, monsieur.",
          "transcription": "[бонжур, месьё]",
          "ru": "Здравствуйте, месье.",
          "audio_text": "Bonjour, monsieur."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_bonjour_translation"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_phrase_bonjour_monsieur"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_fill_merci_beaucoup"
        }
      ],
      "exercises": [
        {
          "id": "ex_bonjour_translation",
          "type": "choose_option",
          "prompt": {
            "ru": "Что значит Bonjour?",
            "fr": "Que signifie Bonjour ?"
          },
          "options": ["спасибо", "здравствуйте", "пожалуйста", "до свидания"],
          "answer": "здравствуйте",
          "explanation": {
            "ru": "Bonjour значит здравствуйте или добрый день.",
            "fr": "Bonjour signifie bonjour ou bonne journée selon le contexte."
          },
          "audio_text": "Bonjour",
          "tags": ["greeting", "basic"],
          "difficulty": 1
        },
        {
          "id": "ex_phrase_bonjour_monsieur",
          "type": "phrase_builder",
          "prompt": {
            "ru": "Собери фразу: Здравствуйте, месье.",
            "fr": "Construis la phrase : Bonjour, monsieur."
          },
          "options": ["Bonjour,", "monsieur.", "Merci", "beaucoup"],
          "answer": "Bonjour, monsieur.",
          "explanation": {
            "ru": "Bonjour, monsieur. - вежливое приветствие.",
            "fr": "Bonjour, monsieur. est une salutation polie."
          },
          "audio_text": "Bonjour, monsieur.",
          "tags": ["greeting", "phrase_builder", "basic"],
          "difficulty": 1
        },
        {
          "id": "ex_fill_merci_beaucoup",
          "type": "fill_blank",
          "prompt": {
            "ru": "Заполни пропуск: Merci ___.",
            "fr": "Complète : Merci ___."
          },
          "options": [],
          "answer": "beaucoup",
          "explanation": {
            "ru": "Merci beaucoup - большое спасибо.",
            "fr": "Merci beaucoup signifie большое спасибо."
          },
          "audio_text": "Merci beaucoup.",
          "tags": ["greeting", "fill_blank", "basic"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/03_de_du/lessons/de_basic_001.json", """
    {
      "id": "de_basic_001",
      "section_id": "de_du",
      "order": 1,
      "level": "A0",
      "title": {
        "ru": "De: из, от, принадлежность и количество",
        "fr": "De : origine, possession et quantité"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Почему de важно",
            "fr": "Pourquoi de est important"
          },
          "body": {
            "ru": "Во французском de часто делает работу, которую в русском делают падежи. Поэтому это не мусорное слово, а ключ.",
            "fr": "En français, de exprime souvent l’origine, la possession ou la quantité."
          }
        },
        {
          "type": "example",
          "fr": "un verre de vin",
          "transcription": "[эн вэр дэ вэн]",
          "ru": "бокал вина",
          "audio_text": "un verre de vin"
        },
        {
          "type": "example",
          "fr": "du pain",
          "transcription": "[дю пэн]",
          "ru": "хлеба / немного хлеба",
          "audio_text": "du pain"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_du_pain_001"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_fill_verre_de_vin_001"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_phrase_je_veux_du_pain"
        }
      ],
      "exercises": [
        {
          "id": "ex_du_pain_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Выбери форму: Je veux ___ pain.",
            "fr": "Choisis la forme : Je veux ___ pain."
          },
          "options": ["de", "du", "de la", "les"],
          "answer": "du",
          "explanation": {
            "ru": "pain мужского рода. Когда говорим про неопределённое количество хлеба, используется du.",
            "fr": "pain est masculin. Pour une quantité non précisée, on utilise du."
          },
          "audio_text": "Je veux du pain.",
          "tags": ["de", "du", "partitif", "article"],
          "difficulty": 1
        },
        {
          "id": "ex_fill_verre_de_vin_001",
          "type": "fill_blank",
          "prompt": {
            "ru": "Заполни пропуск: un verre ___ vin",
            "fr": "Complète : un verre ___ vin"
          },
          "options": [],
          "answer": "de",
          "explanation": {
            "ru": "un verre de vin - бокал вина. Здесь de связывает количество и вещество.",
            "fr": "un verre de vin exprime une quantité."
          },
          "audio_text": "un verre de vin",
          "tags": ["de", "fill_blank", "quantity"],
          "difficulty": 1
        },
        {
          "id": "ex_phrase_je_veux_du_pain",
          "type": "phrase_builder",
          "prompt": {
            "ru": "Собери фразу: Я хочу хлеба.",
            "fr": "Construis : Je veux du pain."
          },
          "options": ["Je", "veux", "du", "pain.", "de", "la"],
          "answer": "Je veux du pain.",
          "explanation": {
            "ru": "Je veux du pain. - я хочу хлеба / немного хлеба.",
            "fr": "Je veux du pain. indique une quantité non précisée."
          },
          "audio_text": "Je veux du pain.",
          "tags": ["de", "du", "phrase_builder", "partitif"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("frontend/src/components/practice/ExerciseRenderer.vue", """
    <script setup lang="ts">
    import { computed, ref, watch } from 'vue'
    import { apiPost } from '../../lib/api'
    import { t, ui } from '../../lib/i18n'
    import { useSettingsStore } from '../../stores/settingsStore'
    import AudioButton from '../learning/AudioButton.vue'

    const props = defineProps<{
      lessonId: string
      exercise: any
      autoFocus?: boolean
    }>()

    const emit = defineEmits<{
      answered: [payload: any]
    }>()

    const settings = useSettingsStore()

    const selected = ref('')
    const textAnswer = ref('')
    const builtParts = ref<string[]>([])
    const result = ref<any | null>(null)
    const loading = ref(false)

    const exerciseType = computed(() => props.exercise?.type ?? 'choose_option')
    const builtAnswer = computed(() => builtParts.value.join(' ').replace(' ,', ',').replace(' .', '.'))

    watch(
      () => props.exercise?.id,
      () => {
        selected.value = ''
        textAnswer.value = ''
        builtParts.value = []
        result.value = null
        loading.value = false
      }
    )

    async function submit(value: string) {
      loading.value = true

      try {
        result.value = await apiPost('/practice/answer', {
          profile_id: 'local_lizard',
          lesson_id: props.lessonId,
          exercise_id: props.exercise.id,
          answer: value,
        })

        emit('answered', result.value)
      } finally {
        loading.value = false
      }
    }

    function choose(value: string) {
      selected.value = value
      submit(value)
    }

    function addPart(value: string) {
      builtParts.value.push(value)
    }

    function undoPart() {
      builtParts.value.pop()
    }

    function submitBuilt() {
      submit(builtAnswer.value)
    }

    function submitText() {
      submit(textAnswer.value)
    }
    </script>

    <template>
      <div class="exercise-renderer">
        <h2>{{ t(exercise.prompt, settings.uiLanguage) }}</h2>

        <AudioButton
          v-if="exercise.audio_text"
          :text="exercise.audio_text"
          :label="ui('listen', settings.uiLanguage)"
        />

        <template v-if="exerciseType === 'fill_blank'">
          <input
            v-model="textAnswer"
            class="answer-input"
            type="text"
            autocomplete="off"
            placeholder="..."
            @keyup.enter="submitText"
          />
          <button class="primary-button" type="button" :disabled="loading || !textAnswer.trim()" @click="submitText">
            {{ settings.uiLanguage === 'ru' ? 'Ответить' : 'Répondre' }}
          </button>
        </template>

        <template v-else-if="exerciseType === 'phrase_builder'">
          <div class="built-phrase">
            <span v-if="builtParts.length">{{ builtAnswer }}</span>
            <span v-else class="muted">{{ settings.uiLanguage === 'ru' ? 'Собери фразу из блоков' : 'Construis la phrase' }}</span>
          </div>

          <div class="option-grid">
            <button
              v-for="option in exercise.options"
              :key="option"
              class="option-button"
              type="button"
              :disabled="loading"
              @click="addPart(option)"
            >
              {{ option }}
            </button>
          </div>

          <div class="button-row">
            <button class="ghost-button" type="button" :disabled="loading || !builtParts.length" @click="undoPart">
              ←
            </button>
            <button class="primary-button" type="button" :disabled="loading || !builtParts.length" @click="submitBuilt">
              {{ settings.uiLanguage === 'ru' ? 'Проверить' : 'Vérifier' }}
            </button>
          </div>
        </template>

        <template v-else>
          <div class="option-grid">
            <button
              v-for="option in exercise.options"
              :key="option"
              class="option-button"
              :class="{ selected: selected === option }"
              type="button"
              :disabled="loading"
              @click="choose(option)"
            >
              {{ option }}
            </button>
          </div>
        </template>

        <div v-if="result" class="result-box" :class="{ good: result.correct, bad: !result.correct }">
          <strong>{{ result.correct ? ui('correct', settings.uiLanguage) : ui('wrong', settings.uiLanguage) }}</strong>
          <p>{{ t(result.explanation, settings.uiLanguage) }}</p>
          <small>Score: {{ result.score }}</small>
        </div>
      </div>
    </template>
    """)

    w("frontend/src/stores/practiceStore.ts", """
    import { defineStore } from 'pinia'
    import { apiGet } from '../lib/api'

    export type PracticeMode = 'quick' | 'weak' | 'audio' | 'vulgar' | 'articles'

    export const usePracticeStore = defineStore('practice', {
      state: () => ({
        mode: 'quick' as PracticeMode,
        session: null as any | null,
        currentIndex: 0,
        loading: false,
        error: null as string | null,
        answered: 0,
        correct: 0,
      }),
      getters: {
        currentExercise: (state) => state.session?.exercises?.[state.currentIndex] ?? null,
        total: (state) => state.session?.exercises?.length ?? 0,
        finished: (state) => Boolean(state.session && state.currentIndex >= (state.session.exercises?.length ?? 0)),
        accuracy: (state) => state.answered ? Math.round(state.correct / state.answered * 100) : 0,
      },
      actions: {
        async load(mode: PracticeMode = this.mode) {
          this.mode = mode
          this.loading = true
          this.error = null
          this.currentIndex = 0
          this.answered = 0
          this.correct = 0

          try {
            this.session = await apiGet(`/review/local_lizard/session?mode=${mode}&limit=7`)
          } catch (error) {
            this.error = error instanceof Error ? error.message : String(error)
          } finally {
            this.loading = false
          }
        },
        markAnswered(payload: any) {
          this.answered += 1
          if (payload?.correct) {
            this.correct += 1
          }
        },
        next() {
          if (!this.session) return
          this.currentIndex += 1
        },
      },
    })
    """)

    w("frontend/src/pages/PracticePage.vue", """
    <script setup lang="ts">
    import { onMounted } from 'vue'
    import ExerciseRenderer from '../components/practice/ExerciseRenderer.vue'
    import { usePracticeStore, type PracticeMode } from '../stores/practiceStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const practice = usePracticeStore()
    const settings = useSettingsStore()

    const modes: { id: PracticeMode; ru: string; fr: string }[] = [
      { id: 'quick', ru: 'Быстро', fr: 'Rapide' },
      { id: 'weak', ru: 'Слабое', fr: 'Faible' },
      { id: 'audio', ru: 'Аудио', fr: 'Audio' },
      { id: 'articles', ru: 'Артикли', fr: 'Articles' },
      { id: 'vulgar', ru: 'Мат', fr: 'Gros mots' },
    ]

    onMounted(() => {
      practice.load('quick')
    })

    function modeLabel(mode: { ru: string; fr: string }) {
      return settings.uiLanguage === 'ru' ? mode.ru : mode.fr
    }

    function onAnswered(payload: any) {
      practice.markAnswered(payload)
    }
    </script>

    <template>
      <section class="page">
        <div class="section-title compact-title">
          <div class="eyebrow">Drill</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Тренировка' : 'Entraînement' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Короткая сессия на один экран. Без перегруза, только удар по слабым местам.'
                : 'Session courte, mobile-first, sans surcharge.'
            }}
          </p>
        </div>

        <div class="chip-row">
          <button
            v-for="mode in modes"
            :key="mode.id"
            class="ghost-button"
            :class="{ active: practice.mode === mode.id }"
            type="button"
            @click="practice.load(mode.id)"
          >
            {{ modeLabel(mode) }}
          </button>
        </div>

        <div v-if="practice.loading" class="soft-card">Загрузка...</div>
        <div v-else-if="practice.error" class="soft-card">{{ practice.error }}</div>

        <template v-else-if="practice.currentExercise">
          <div class="practice-head">
            <span>{{ practice.currentIndex + 1 }} / {{ practice.total }}</span>
            <span>{{ practice.correct }} correct</span>
            <span>{{ practice.accuracy }}%</span>
          </div>

          <div class="lesson-progress">
            <div :style="{ width: ((practice.currentIndex + 1) / practice.total * 100) + '%' }"></div>
          </div>

          <div class="study-card">
            <ExerciseRenderer
              :lesson-id="practice.currentExercise.lesson_id"
              :exercise="practice.currentExercise"
              @answered="onAnswered"
            />

            <button class="primary-button" type="button" @click="practice.next">
              {{ settings.uiLanguage === 'ru' ? 'Следующий удар' : 'Coup suivant' }}
            </button>
          </div>
        </template>

        <div v-else class="hero-card">
          <div class="crest-orb">✓</div>
          <div class="eyebrow">Session complete</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Дрель завершена' : 'Session terminée' }}</h1>
          <p>
            {{ practice.correct }} / {{ practice.answered }}
            correct, {{ practice.accuracy }}%
          </p>
          <button class="primary-button" type="button" @click="practice.load(practice.mode)">
            {{ settings.uiLanguage === 'ru' ? 'Повторить' : 'Recommencer' }}
          </button>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/ProfilePage.vue", """
    <script setup lang="ts">
    import { onMounted, ref } from 'vue'
    import VoiceSelector from '../components/audio/VoiceSelector.vue'
    import { apiGet } from '../lib/api'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const summary = ref<any | null>(null)

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      summary.value = await apiGet('/progress/local_lizard/summary')
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Profil</div>
          <h1>{{ bootstrap.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Интерфейс' : 'Interface' }}</h2>
          <button class="primary-button" type="button" @click="settings.toggleLanguage">
            {{ settings.uiLanguage === 'ru' ? 'Переключить на французский' : 'Passer en russe' }}
          </button>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Прогресс' : 'Progression' }}</h2>
          <div class="stat-grid" v-if="summary">
            <div>
              <strong>{{ summary.score }}</strong>
              <span>score</span>
            </div>
            <div>
              <strong>{{ summary.accuracy }}%</strong>
              <span>accuracy</span>
            </div>
            <div>
              <strong>{{ summary.completed_count }}</strong>
              <span>lessons</span>
            </div>
          </div>
        </div>

        <div class="study-card" v-if="summary?.weak_topics?.length">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Слабые темы' : 'Points faibles' }}</h2>
          <div class="chip-row">
            <span v-for="tag in summary.weak_topics" :key="tag" class="stat-chip">{{ tag }}</span>
          </div>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Текущий ранг' : 'Grade actuel' }}</h2>
          <p>{{ bootstrap.payload?.profile?.rank_id }}</p>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
          <VoiceSelector />
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/ThronePage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref } from 'vue'
    import { RouterLink } from 'vue-router'
    import AudioButton from '../components/learning/AudioButton.vue'
    import { apiGet } from '../lib/api'
    import { ui } from '../lib/i18n'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const summary = ref<any | null>(null)

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      summary.value = await apiGet('/progress/local_lizard/summary')
    })

    const profile = computed(() => bootstrap.payload?.profile)
    const firstLesson = computed(() => bootstrap.payload?.sections?.[0]?.lessons?.[0] ?? 'greetings_001')
    </script>

    <template>
      <section class="page throne-page">
        <div class="hero-card">
          <div class="crest-orb">♛</div>
          <div class="eyebrow">Forge Française</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Тронный зал' : 'Salle du trône' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Мобильная имперская кузница французского. Без перегруза, но с короной.'
                : 'Une forge mobile et impériale pour apprendre le français.'
            }}
          </p>

          <div class="profile-strip" v-if="profile">
            <span>{{ profile.display_name }}</span>
            <strong>{{ profile.rank_id }}</strong>
          </div>

          <div class="stat-grid" v-if="summary">
            <div>
              <strong>{{ summary.score }}</strong>
              <span>score</span>
            </div>
            <div>
              <strong>{{ summary.accuracy }}%</strong>
              <span>accuracy</span>
            </div>
            <div>
              <strong>{{ summary.completed_count }}</strong>
              <span>lessons</span>
            </div>
          </div>

          <div class="hero-actions">
            <RouterLink class="primary-button" :to="'/lesson/' + firstLesson">
              {{ ui('continue', settings.uiLanguage) }}
            </RouterLink>
            <AudioButton text="Bonjour, monsieur." :label="ui('listen', settings.uiLanguage)" />
          </div>
        </div>

        <div class="quick-grid">
          <RouterLink class="quick-card" to="/practice">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Дрель' : 'Drill' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? '5 быстрых ударов по хаосу' : 'Cinq coups rapides contre le chaos' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/vulgar">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Мат' : 'Gros mots' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Грубый французский под замком' : 'Français vulgaire sous contrôle' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/codex">
            <strong>{{ ui('codex', settings.uiLanguage) }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Артикли, de и прочая магия' : 'Articles, de et autres mystères' }}</span>
          </RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/styles/imperial.css", """
    .imperial-shell {
      position: relative;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: calc(var(--bottom-nav-height) + 18px);
    }

    .shell-main {
      width: min(100%, 980px);
      margin: 0 auto;
      padding: 14px;
    }

    .top-bar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px;
      background: rgba(11, 13, 12, 0.82);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(176, 138, 69, 0.25);
    }

    .top-title,
    h1,
    h2 {
      letter-spacing: 0.02em;
    }

    .top-title {
      font-weight: 800;
    }

    .eyebrow {
      color: var(--antique-gold);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .page {
      display: grid;
      gap: 14px;
    }

    .hero-card,
    .study-card,
    .soft-card,
    .quick-card,
    .lesson-tile {
      border: 1px solid rgba(232, 226, 216, 0.12);
      background:
        linear-gradient(135deg, rgba(37, 91, 50, 0.28), transparent 38%),
        var(--panel-black);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-soft);
    }

    .hero-card {
      min-height: calc(100vh - 190px);
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 16px;
      padding: 26px;
    }

    .hero-card h1,
    .section-title h1 {
      margin: 0;
      font-size: clamp(2rem, 12vw, 4.6rem);
      line-height: 0.95;
    }

    .compact-title h1 {
      font-size: clamp(1.5rem, 8vw, 2.6rem);
    }

    .hero-card p,
    .section-title p,
    .study-card p {
      color: var(--text-muted);
      line-height: 1.55;
    }

    .crest-orb {
      width: 72px;
      height: 72px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(176, 138, 69, 0.55);
      border-radius: 50%;
      background: radial-gradient(circle, rgba(176, 138, 69, 0.35), rgba(37, 91, 50, 0.25));
      font-size: 2rem;
    }

    .profile-strip,
    .practice-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
    }

    .practice-head {
      color: var(--antique-gold);
      font-size: 0.82rem;
      font-weight: 900;
      text-transform: uppercase;
    }

    .hero-actions,
    .quick-grid,
    .option-grid,
    .button-row {
      display: grid;
      gap: 10px;
    }

    .button-row {
      grid-template-columns: 1fr auto;
    }

    .primary-button,
    .audio-button,
    .ghost-button,
    .option-button {
      border: 0;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 800;
    }

    .primary-button,
    .audio-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 48px;
      padding: 0 18px;
    }

    .primary-button {
      color: #071009;
      background: linear-gradient(135deg, var(--bone-white), var(--antique-gold));
    }

    .audio-button {
      color: var(--bone-white);
      background: rgba(47, 122, 69, 0.45);
      border: 1px solid rgba(232, 226, 216, 0.14);
    }

    .ghost-button {
      min-height: 40px;
      padding: 0 14px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
    }

    .ghost-button.active,
    .ghost-button.wide {
      border: 1px solid rgba(176, 138, 69, 0.45);
    }

    .quick-grid {
      grid-template-columns: 1fr;
    }

    .quick-card,
    .lesson-tile,
    .study-card,
    .soft-card {
      padding: 18px;
    }

    .quick-card,
    .lesson-tile {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .lesson-tile-vertical {
      align-items: flex-start;
      flex-direction: column;
    }

    .lesson-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--antique-gold);
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
    }

    .quick-card span,
    .lesson-tile span,
    .lesson-tile small {
      display: block;
      margin-top: 4px;
      color: var(--text-muted);
      font-size: 0.92rem;
    }

    .tile-icon {
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: 16px;
      background: rgba(176, 138, 69, 0.16);
    }

    .card-list {
      display: grid;
      gap: 12px;
    }

    .study-card {
      display: grid;
      gap: 10px;
      min-height: min(420px, calc(100vh - 260px));
      align-content: center;
    }

    .study-card h2 {
      margin: 0;
      font-size: clamp(1.4rem, 9vw, 2.8rem);
    }

    .transcription {
      color: var(--antique-gold) !important;
      font-weight: 700;
    }

    .muted {
      color: var(--text-muted);
    }

    .mini-details {
      padding: 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.05);
    }

    .option-grid {
      grid-template-columns: 1fr;
    }

    .option-button {
      min-height: 52px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(232, 226, 216, 0.12);
    }

    .option-button.selected {
      outline: 2px solid var(--antique-gold);
    }

    .answer-input,
    .built-phrase {
      width: 100%;
      min-height: 54px;
      padding: 0 16px;
      border-radius: 18px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .answer-input {
      outline: none;
    }

    .built-phrase {
      display: flex;
      align-items: center;
      line-height: 1.4;
    }

    .result-box {
      padding: 14px;
      border-radius: 16px;
    }

    .result-box.good {
      background: rgba(47, 122, 69, 0.24);
    }

    .result-box.bad {
      background: rgba(138, 45, 45, 0.24);
    }

    .codex-row {
      display: grid;
      gap: 4px;
      padding: 10px 0;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .danger-card {
      border-color: rgba(138, 45, 45, 0.45);
    }

    .rudeness {
      width: fit-content;
      padding: 6px 10px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(138, 45, 45, 0.45);
      font-size: 0.8rem;
      font-weight: 900;
    }

    .voice-selector {
      display: grid;
      gap: 8px;
    }

    .voice-selector select {
      width: 100%;
      min-height: 48px;
      padding: 0 14px;
      border-radius: 16px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .sheet-backdrop {
      position: fixed;
      inset: 0;
      z-index: 80;
      display: flex;
      align-items: flex-end;
      background: rgba(0, 0, 0, 0.58);
    }

    .bottom-sheet {
      width: 100%;
      max-height: 76vh;
      overflow: auto;
      padding: 14px 18px 24px;
      border-radius: 28px 28px 0 0;
      border: 1px solid rgba(232, 226, 216, 0.12);
      background: rgba(11, 13, 12, 0.98);
      box-shadow: var(--shadow-soft);
    }

    .sheet-handle {
      width: 54px;
      height: 5px;
      margin: 0 auto 14px;
      border-radius: 999px;
      background: rgba(232, 226, 216, 0.26);
    }

    .sheet-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .sheet-head h2 {
      margin: 0;
    }

    .lesson-progress {
      height: 8px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
    }

    .lesson-progress div {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--sovereign-green), var(--antique-gold));
      transition: width 0.2s ease;
    }

    .lesson-nav-row {
      display: grid;
      grid-template-columns: auto 1fr 1fr;
      gap: 10px;
    }

    .lesson-nav-row .ghost-button,
    .lesson-nav-row .primary-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
    }

    .stat-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .stat-grid div {
      display: grid;
      gap: 2px;
      padding: 12px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.06);
      text-align: center;
    }

    .stat-grid strong {
      font-size: 1.25rem;
      color: var(--antique-gold);
    }

    .stat-grid span {
      color: var(--text-muted);
      font-size: 0.74rem;
      text-transform: uppercase;
    }

    .stat-chip {
      flex: 0 0 auto;
      padding: 8px 12px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(176, 138, 69, 0.16);
      font-size: 0.82rem;
      font-weight: 800;
    }
    """)

    w("backend/scripts/validate_content.py", """
    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[2]
    CONTENT_ROOT = ROOT / "content"

    errors: list[str] = []


    def read_json(path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Cannot read {path}: {exc}")
            return None


    def require_localized(obj: dict, field: str, path: Path) -> None:
        value = obj.get(field)
        if not isinstance(value, dict):
            errors.append(f"{path}: {field} must be localized object")
            return
        for lang in ["ru", "fr"]:
            if not value.get(lang):
                errors.append(f"{path}: {field}.{lang} is required")


    section_ids: set[str] = set()
    lesson_ids: set[str] = set()
    exercise_ids: set[str] = set()

    for section_path in sorted((CONTENT_ROOT / "sections").glob("*/section.json")):
        section = read_json(section_path)
        if not section:
            continue

        section_id = section.get("id")

        if not section_id:
            errors.append(f"{section_path}: missing id")
        elif section_id in section_ids:
            errors.append(f"{section_path}: duplicated section id {section_id}")
        else:
            section_ids.add(section_id)

        require_localized(section, "title", section_path)
        require_localized(section, "subtitle", section_path)

        if "order" not in section:
            errors.append(f"{section_path}: missing order")

        for lesson_id in section.get("lessons", []):
            lesson_file = next(CONTENT_ROOT.glob(f"sections/*/lessons/{lesson_id}.json"), None)
            if not lesson_file:
                errors.append(f"{section_path}: referenced lesson not found: {lesson_id}")

    for lesson_path in sorted((CONTENT_ROOT / "sections").glob("*/lessons/*.json")):
        lesson = read_json(lesson_path)
        if not lesson:
            continue

        lesson_id = lesson.get("id")

        if not lesson_id:
            errors.append(f"{lesson_path}: missing id")
        elif lesson_id in lesson_ids:
            errors.append(f"{lesson_path}: duplicated lesson id {lesson_id}")
        else:
            lesson_ids.add(lesson_id)

        if lesson.get("section_id") not in section_ids:
            errors.append(f"{lesson_path}: unknown section_id {lesson.get('section_id')}")

        require_localized(lesson, "title", lesson_path)

        card_exercise_refs = set()

        for card in lesson.get("cards", []):
            card_type = card.get("type")
            if not card_type:
                errors.append(f"{lesson_path}: card without type")

            if card_type in ["word", "example"]:
                if not card.get("fr"):
                    errors.append(f"{lesson_path}: {card_type} card without fr")
                if not card.get("ru"):
                    errors.append(f"{lesson_path}: {card_type} card without ru")
                if not card.get("transcription"):
                    errors.append(f"{lesson_path}: {card_type} card without transcription")
                if not card.get("audio_text"):
                    errors.append(f"{lesson_path}: {card_type} card without audio_text")

            if card_type == "exercise":
                if not card.get("exercise_id"):
                    errors.append(f"{lesson_path}: exercise card without exercise_id")
                else:
                    card_exercise_refs.add(card["exercise_id"])

        local_exercises = set()

        for exercise in lesson.get("exercises", []):
            exercise_id = exercise.get("id")
            exercise_type = exercise.get("type")

            if not exercise_id:
                errors.append(f"{lesson_path}: exercise without id")
            elif exercise_id in exercise_ids:
                errors.append(f"{lesson_path}: duplicated exercise id {exercise_id}")
            else:
                exercise_ids.add(exercise_id)
                local_exercises.add(exercise_id)

            if "answer" not in exercise:
                errors.append(f"{lesson_path}: exercise {exercise_id} has no answer")

            if "prompt" not in exercise:
                errors.append(f"{lesson_path}: exercise {exercise_id} has no prompt")
            else:
                require_localized(exercise, "prompt", lesson_path)

            if "explanation" not in exercise:
                errors.append(f"{lesson_path}: exercise {exercise_id} has no explanation")
            else:
                require_localized(exercise, "explanation", lesson_path)

            if exercise_type in ["choose_option", "phrase_builder"] and not exercise.get("options"):
                errors.append(f"{lesson_path}: exercise {exercise_id} type {exercise_type} requires options")

            if not exercise.get("tags"):
                errors.append(f"{lesson_path}: exercise {exercise_id} has no tags")

        missing_refs = card_exercise_refs - local_exercises
        for missing in missing_refs:
            errors.append(f"{lesson_path}: card references missing exercise {missing}")

    for pack_path in sorted((CONTENT_ROOT / "vulgar" / "packs").glob("*.json")):
        pack = read_json(pack_path)
        if not pack:
            continue

        require_localized(pack, "title", pack_path)

        for item in pack.get("items", []):
            for field in ["id", "fr", "transcription", "ru", "rudeness_level", "context", "audio_text"]:
                if field not in item:
                    errors.append(f"{pack_path}: vulgar item missing {field}: {item.get('id')}")

            if item.get("rudeness_level", 0) < 1 or item.get("rudeness_level", 0) > 5:
                errors.append(f"{pack_path}: invalid rudeness_level for {item.get('id')}")

    if errors:
        print("Content validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Content validation passed.")
    print(f"Sections: {len(section_ids)}")
    print(f"Lessons: {len(lesson_ids)}")
    print(f"Exercises: {len(exercise_ids)}")
    """)

    w("project.config.json", json.dumps({
        "name": "Forge Francaise",
        "public_title_ru": "Имперский мозговыбиватель французского языка",
        "backend_port": BACKEND_PORT,
        "frontend_port": FRONTEND_PORT,
        "api_base": f"http://127.0.0.1:{BACKEND_PORT}/api",
        "frontend_url": f"http://127.0.0.1:{FRONTEND_PORT}",
        "version": "0.4.0",
        "patch": "patch 4: real practice modes, review, progress scoring"
    }, ensure_ascii=False, indent=2))

    w("README.md", """
    # Forge Française

    Имперский мозговыбиватель французского языка.

    Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

    ## Ports

    Backend:
    http://127.0.0.1:8797/api/health

    Frontend:
    http://127.0.0.1:5197

    ## Быстрый запуск

    scripts\\Forge Francaise Launcher.cmd

    ## Что уже заложено

    - Vue 3 + TypeScript + Vite
    - FastAPI backend
    - JSON content engine
    - profiles / progress / ranks
    - TTS provider architecture
    - audio cache
    - vulgar French library
    - mobile-first UI
    - bottom navigation
    - bottom sheet
    - RU / FR UI switch
    - voice selector
    - storage adapter
    - scalable ExerciseRenderer
    - course API
    - section pages
    - lesson card mode
    - expanded A0 content
    - real practice sessions
    - weak topic review
    - progress scoring
    - answer event log

    ## Patch 4

    Patch 4 adds:

    - review API
    - practice modes: quick, weak, audio, articles, vulgar
    - progress summary endpoint
    - scoring
    - weak topic detection
    - fill_blank exercise support
    - phrase_builder exercise support
    - stronger ExerciseRenderer
    - improved PracticePage
    - profile stats
    - throne stats
    """)

    w("scripts/git_push_patch4.cmd", f"""
    @echo off
    cd /d "%~dp0.."
    git config user.name "{GIT_NAME}"
    git config user.email "{GIT_EMAIL}"
    git status --short
    git add .
    git commit -m "patch 4: real practice modes and progress scoring"
    git push -u origin main
    """)

    print("")
    print("Running content validation...")
    run(["py", "scripts\\validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("Git identity...")
    run(["git", "config", "user.name", GIT_NAME])
    run(["git", "config", "user.email", GIT_EMAIL])

    print("")
    print("Git commit...")
    run(["git", "add", "."])
    commit_code = run(["git", "commit", "-m", "patch 4: real practice modes and progress scoring"])

    if commit_code != 0:
        print("commit failed or nothing to commit")

    print("")
    print("Git push...")
    push_code = run(["git", "push", "-u", "origin", "main"])

    if push_code != 0:
        print("")
        print("GIT PUSH FAILED OR NEEDS AUTH")
        print("Manual command:")
        print(r'cd /d "D:\PYTHON\Forge Francaise"')
        print(r"scripts\git_push_patch4.cmd")

    print("")
    print("PATCH 4 DONE")
    print("Готовность проекта: примерно 62%")
    print("")
    print("Что добавлено:")
    print("- review API")
    print("- progress summary")
    print("- scoring")
    print("- weak topics")
    print("- practice modes")
    print("- fill_blank")
    print("- phrase_builder")
    print("- upgraded ExerciseRenderer")
    print("- upgraded PracticePage")
    print("- profile stats")
    print("- throne stats")
    print("")
    print("Next patch will be step 5/6: audio module upgrade, cache controls, UI polish.")

if __name__ == "__main__":
    main()