from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_tokenize_tiktoken_success_shape():
    response = client.post(
        "/api/tokenize",
        data={
            "tokenizer_mode": "tiktoken",
            "text": "Hello, world!",
            "encoding": "cl100k_base",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tokenizer_mode"] == "tiktoken"
    assert body["encoding"] == "cl100k_base"
    assert isinstance(body["tokens"], list)
    assert len(body["tokens"]) > 0
    for token in body["tokens"]:
        assert set(token.keys()) == {"index", "id", "text", "start", "end", "is_new"}
        assert token["is_new"] is None
    stats = body["stats"]
    assert set(stats.keys()) == {
        "character_count",
        "word_count",
        "token_count",
        "tokens_per_word",
        "tokens_per_character",
    }


def test_tokenize_empty_text_returns_empty_input_error():
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "text": "   ", "encoding": "cl100k_base"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "EMPTY_INPUT"
    assert body["message"]


def test_tokenize_unsupported_encoding_returns_error():
    response = client.post(
        "/api/tokenize",
        data={
            "tokenizer_mode": "tiktoken",
            "text": "Hello",
            "encoding": "not-a-real-encoding",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "UNSUPPORTED_ENCODING"


def test_tokenize_no_text_and_no_file_returns_empty_input_error():
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "EMPTY_INPUT"


def test_tokenize_custom_success_shape():
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "custom", "text": "Hello, world!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tokenizer_mode"] == "custom"
    assert body["encoding"] is None
    assert len(body["tokens"]) > 0
    for token in body["tokens"]:
        assert isinstance(token["is_new"], bool)


def test_tokenize_rejects_both_text_and_file_present():
    with open(FIXTURES / "sample.txt", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "text": "also has text", "encoding": "cl100k_base"},
            files={"file": ("sample.txt", fh, "text/plain")},
        )
    assert response.status_code == 400


def test_tokenize_file_unsupported_type_returns_error():
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
        files={"file": ("image.png", b"\x89PNG\r\n", "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "UNSUPPORTED_FILE_TYPE"


def test_tokenize_file_oversized_returns_error():
    oversized = b"a" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
        files={"file": ("big.txt", oversized, "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "FILE_TOO_LARGE"


def test_tokenize_corrupted_pdf_returns_error():
    with open(FIXTURES / "corrupted.pdf", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("corrupted.pdf", fh, "application/pdf")},
        )
    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_PDF"


def test_tokenize_whitespace_only_txt_file_returns_empty_input_error():
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
        files={"file": ("blank.txt", b"   \n\t  ", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "EMPTY_INPUT"


def test_tokenize_bpe_mode_before_training_returns_error():
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "bpe", "text": "abc"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_MODEL_NOT_TRAINED"


def test_tokenize_bpe_mode_success_shape():
    client.post("/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9})

    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "bpe", "text": "aaabac"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tokenizer_mode"] == "bpe"
    assert body["encoding"] is None
    assert len(body["tokens"]) > 0
    for token in body["tokens"]:
        assert token["is_new"] is False


def test_tokenize_bpe_mode_unknown_character_returns_error():
    client.post("/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9})

    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "bpe", "text": "xyz"},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_UNKNOWN_CHARACTER"


def test_tokenize_no_text_pdf_returns_error():
    with open(FIXTURES / "image_only.pdf", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("image_only.pdf", fh, "application/pdf")},
        )
    assert response.status_code == 400
    assert response.json()["error_code"] == "PDF_NO_TEXT"
