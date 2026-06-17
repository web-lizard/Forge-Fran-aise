from typing import Any

from app.services.content_service import get_content_service


class CourseService:
    def course_map(self) -> dict[str, Any]:
        content = get_content_service()
        sections = content.list_sections()
        result_sections = []

        for section in sections:
            lessons = []
            for lesson_id in section.get("lessons", []):
                lesson = content.get_lesson(lesson_id)
                lessons.append({
                    "id": lesson["id"],
                    "section_id": lesson["section_id"],
                    "order": lesson.get("order", 999),
                    "level": lesson.get("level", "A0"),
                    "title": lesson["title"],
                    "card_count": len(lesson.get("cards", [])),
                    "exercise_count": len(lesson.get("exercises", [])),
                })

            item = dict(section)
            item["lesson_items"] = sorted(lessons, key=lambda lesson: lesson.get("order", 999))
            result_sections.append(item)

        return {
            "sections": result_sections,
            "total_sections": len(result_sections),
            "total_lessons": sum(len(section["lesson_items"]) for section in result_sections),
        }

    def section_with_lessons(self, section_id: str) -> dict[str, Any]:
        content = get_content_service()
        section = dict(content.get_section(section_id))
        lessons = []

        for lesson_id in section.get("lessons", []):
            lesson = content.get_lesson(lesson_id)
            lessons.append({
                "id": lesson["id"],
                "section_id": lesson["section_id"],
                "order": lesson.get("order", 999),
                "level": lesson.get("level", "A0"),
                "title": lesson["title"],
                "card_count": len(lesson.get("cards", [])),
                "exercise_count": len(lesson.get("exercises", [])),
            })

        section["lesson_items"] = sorted(lessons, key=lambda lesson: lesson.get("order", 999))
        return section


def get_course_service() -> CourseService:
    return CourseService()
