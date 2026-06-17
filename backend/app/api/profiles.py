from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.profile_service import get_profile_service

router = APIRouter(tags=["profiles"])


@router.get("/profiles")
def list_profiles():
    return get_profile_service().list_profiles()


@router.get("/profiles/active")
def active_profile():
    return get_profile_service().active_profile()


@router.patch("/profiles/{profile_id}")
def update_profile(profile_id: str, patch: dict[str, Any]):
    try:
        return get_profile_service().update_profile(profile_id, patch)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
