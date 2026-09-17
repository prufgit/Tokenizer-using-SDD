from typing import Literal

from pydantic import BaseModel

TokenizerMode = Literal["tiktoken", "custom", "bpe"]


class Token(BaseModel):
    index: int
    id: int
    text: str
    start: int
    end: int
    is_new: bool | None = None


class Statistics(BaseModel):
    character_count: int
    word_count: int
    token_count: int
    tokens_per_word: float
    tokens_per_character: float


class TokenizeResponse(BaseModel):
    tokenizer_mode: TokenizerMode
    encoding: str | None
    tokens: list[Token]
    stats: Statistics
