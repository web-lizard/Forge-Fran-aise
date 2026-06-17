from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["codex"])


@router.get("/codex")
def list_codex():
    return get_content_service().list_codex()


@router.get("/codex/{entry_id}")
def get_codex_entry(entry_id: str):
    try:
        return get_content_service().get_codex_entry(entry_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
