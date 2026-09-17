from fastapi import APIRouter

from app.schemas.encodings import EncodingsResponse
from app.services import tiktoken_service

router = APIRouter()


@router.get("/api/encodings", response_model=EncodingsResponse)
def get_encodings() -> EncodingsResponse:
    return EncodingsResponse(encodings=tiktoken_service.list_encodings())
