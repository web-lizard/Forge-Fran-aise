from fastapi import APIRouter

from app.services.diagnostic_service import get_diagnostic_service

router = APIRouter(tags=["diagnostics"])


@router.get("/diagnostics")
def diagnostics():
    return get_diagnostic_service().app_diagnostics()
