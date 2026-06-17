from fastapi import APIRouter

from app.core.config import config

router = APIRouter(tags=["settings"])


@router.get("/settings")
def get_settings():
    return config.model_dump()
