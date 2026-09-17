from fastapi import APIRouter

from app.schemas.vocabulary import CustomVocabularyEntry, VocabularyResponse
from app.services.vocabulary_store import vocabulary_store

router = APIRouter()


def _to_response() -> VocabularyResponse:
    entries = [
        CustomVocabularyEntry(
            id=entry.id,
            token=entry.token,
            frequency=entry.frequency,
            status="new" if entry.token in vocabulary_store.last_new_tokens else "existing",
        )
        for entry in vocabulary_store.entries()
    ]
    return VocabularyResponse(entries=entries, total_entries=len(entries))


@router.get("/api/vocabulary", response_model=VocabularyResponse)
def get_vocabulary() -> VocabularyResponse:
    return _to_response()


@router.post("/api/vocabulary/reset", response_model=VocabularyResponse)
def post_reset_vocabulary() -> VocabularyResponse:
    vocabulary_store.reset()
    return _to_response()
