from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["sections"])


@router.get("/sections")
def list_sections():
    return get_content_service().list_sections()


@router.get("/sections/{section_id}")
def get_section(section_id: str):
    try:
        return get_content_service().get_section(section_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
