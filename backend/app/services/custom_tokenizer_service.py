import re

from app.schemas.tokenize import Token
from app.services.vocabulary_store import VocabularyStore

_TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]")


def tokenize(text: str, store: VocabularyStore) -> list[Token]:
    """Deterministic Custom Tokenizer: whitespace/punctuation split (FR-010).

    Each match is a "word" run (letters/digits/underscore) or a single
    punctuation/symbol character; whitespace is never emitted as a token. IDs are
    reused from `store` when a token is already known, or created deterministically
    otherwise (FR-012-FR-014). Every occurrence of a token that was unseen before
    this call is flagged `is_new=True`, even if it repeats within this same
    operation (FR-016; spec Edge Cases).
    """
    matches = list(_TOKEN_PATTERN.finditer(text))
    token_texts = [m.group(0) for m in matches]

    newly_created_this_op: set[str] = set()
    for token_text in token_texts:
        if token_text not in store.token_to_id:
            store.get_or_create_id(token_text)
            newly_created_this_op.add(token_text)

    tokens: list[Token] = []
    for index, match in enumerate(matches):
        token_text = match.group(0)
        store.record_occurrence(token_text)
        tokens.append(
            Token(
                index=index,
                id=store.token_to_id[token_text],
                text=token_text,
                start=match.start(),
                end=match.end(),
                is_new=token_text in newly_created_this_op,
            )
        )

    store.last_new_tokens = newly_created_this_op
    return tokens
