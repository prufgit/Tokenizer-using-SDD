import tiktoken

from app.services import tiktoken_service


def test_list_encodings_matches_tiktoken_library():
    assert tiktoken_service.list_encodings() == tiktoken.list_encoding_names()


def test_tokenize_returns_real_ids_and_text_for_cl100k_base():
    text = "Hello, world!"
    encoding = tiktoken.get_encoding("cl100k_base")
    expected_ids = encoding.encode(text)

    tokens = tiktoken_service.tokenize(text, "cl100k_base")

    assert [t.id for t in tokens] == expected_ids
    assert "".join(t.text for t in tokens) == text
    for t in tokens:
        assert t.is_new is None


def test_tokenize_returns_real_ids_for_second_encoding():
    text = "The quick brown fox jumps over the lazy dog."
    encoding = tiktoken.get_encoding("o200k_base")
    expected_ids = encoding.encode(text)

    tokens = tiktoken_service.tokenize(text, "o200k_base")

    assert [t.id for t in tokens] == expected_ids


def test_tokenize_offsets_are_contiguous_and_cover_full_text():
    text = "Hello, world!"
    tokens = tiktoken_service.tokenize(text, "cl100k_base")

    assert tokens[0].start == 0
    assert tokens[-1].end == len(text)
    for prev, curr in zip(tokens, tokens[1:]):
        assert curr.start == prev.end


def test_tokenize_handles_multibyte_characters_split_across_tokens():
    # Multi-byte UTF-8 text (emoji + accented characters) exercises the
    # incremental decoder path from research.md decision 4.
    text = "café \U0001F600 你好"
    tokens = tiktoken_service.tokenize(text, "cl100k_base")

    reconstructed = "".join(t.text for t in tokens)
    assert reconstructed == text
    assert tokens[-1].end == len(text)


def test_require_supported_encoding_accepts_known_encoding():
    from app.services.tiktoken_service import require_supported_encoding

    assert require_supported_encoding("cl100k_base") == "cl100k_base"


def test_require_supported_encoding_rejects_unknown_encoding():
    import pytest

    from app.core.errors import UnsupportedEncodingError
    from app.services.tiktoken_service import require_supported_encoding

    with pytest.raises(UnsupportedEncodingError):
        require_supported_encoding("not-a-real-encoding")
