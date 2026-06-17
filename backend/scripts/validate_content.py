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
