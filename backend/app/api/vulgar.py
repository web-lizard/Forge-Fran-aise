from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["vulgar"])


@router.get("/vulgar/categories")
def categories():
    return get_content_service().vulgar_index()


@router.get("/vulgar/items")
def items():
    return get_content_service().list_vulgar_items()


@router.get("/vulgar/items/{item_id}")
def item(item_id: str):
    try:
        return get_content_service().get_vulgar_item(item_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
