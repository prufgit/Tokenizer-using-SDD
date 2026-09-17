from typing import Literal

from pydantic import BaseModel

VocabularyEntryStatus = Literal["new", "existing"]


class CustomVocabularyEntry(BaseModel):
    id: int
    token: str
    frequency: int
    status: VocabularyEntryStatus


class VocabularyResponse(BaseModel):
    entries: list[CustomVocabularyEntry]
    total_entries: int
