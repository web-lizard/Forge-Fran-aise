from fastapi import APIRouter, HTTPException

from app.services.course_service import get_course_service

router = APIRouter(tags=["course"])


@router.get("/course")
def course_map():
    return get_course_service().course_map()


@router.get("/course/sections/{section_id}")
def section_with_lessons(section_id: str):
    try:
        return get_course_service().section_with_lessons(section_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
