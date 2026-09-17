import codecs

import tiktoken

from app.core.errors import UnsupportedEncodingError
from app.schemas.tokenize import Token


def list_encodings() -> list[str]:
    """Live from the installed tiktoken library — never hardcoded (FR-026)."""
    return tiktoken.list_encoding_names()


def require_supported_encoding(encoding_name: str | None) -> str:
    supported = list_encodings()
    if not encoding_name or encoding_name not in supported:
        raise UnsupportedEncodingError(
            f"'{encoding_name}' is not a supported Tiktoken encoding. "
            f"Supported encodings: {', '.join(supported)}."
        )
    return encoding_name


def tokenize(text: str, encoding_name: str) -> list[Token]:
    """Real Tiktoken tokens/IDs for `encoding_name`, with character offsets.

    Token byte boundaries don't always align with whole characters, so offsets are
    derived with an incremental UTF-8 decoder that buffers partial multi-byte
    sequences across token boundaries (research.md decision 4).
    """
    encoding = tiktoken.get_encoding(encoding_name)
    token_ids = encoding.encode(text)

    tokens: list[Token] = []
    decoder = codecs.getincrementaldecoder("utf-8")()
    offset = 0

    for index, token_id in enumerate(token_ids):
        token_bytes = encoding.decode_single_token_bytes(token_id)
        decoded_piece = decoder.decode(token_bytes)
        start = offset
        end = offset + len(decoded_piece)
        tokens.append(
            Token(
                index=index,
                id=token_id,
                text=decoded_piece,
                start=start,
                end=end,
                is_new=None,
                bytes=list(token_bytes),
            )
        )
        offset = end

    return tokens
