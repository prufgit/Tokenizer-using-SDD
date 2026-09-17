from app.schemas.tokenize import Statistics


def compute_statistics(text: str, token_count: int) -> Statistics:
    """Character/word/token counts and ratios, shared by every tokenizer mode (FR-008)."""
    character_count = len(text)
    word_count = len(text.split())

    tokens_per_word = token_count / word_count if word_count > 0 else 0.0
    tokens_per_character = (
        token_count / character_count if character_count > 0 else 0.0
    )

    return Statistics(
        character_count=character_count,
        word_count=word_count,
        token_count=token_count,
        tokens_per_word=tokens_per_word,
        tokens_per_character=tokens_per_character,
    )
