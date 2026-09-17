from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    "error_code, make_request",
    [
        (
            "EMPTY_INPUT",
            lambda: client.post(
                "/api/tokenize", data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"}
            ),
        ),
        (
            "UNSUPPORTED_ENCODING",
            lambda: client.post(
                "/api/tokenize",
                data={"tokenizer_mode": "tiktoken", "text": "hi", "encoding": "bogus"},
            ),
        ),
        (
            "UNSUPPORTED_FILE_TYPE",
            lambda: client.post(
                "/api/tokenize",
                data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
                files={"file": ("image.png", b"\x89PNG", "image/png")},
            ),
        ),
        (
            "FILE_TOO_LARGE",
            lambda: client.post(
                "/api/tokenize",
                data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
                files={"file": ("big.txt", b"a" * (10 * 1024 * 1024 + 1), "text/plain")},
            ),
        ),
    ],
)
def test_error_scenario_returns_distinct_error_code_and_message(error_code, make_request):
    response = make_request()
    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == error_code
    assert isinstance(body["message"], str) and len(body["message"]) > 0


def test_invalid_pdf_scenario():
    with open(FIXTURES / "corrupted.pdf", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("corrupted.pdf", fh, "application/pdf")},
        )
    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "INVALID_PDF"
    assert body["message"]


def test_pdf_no_text_scenario():
    with open(FIXTURES / "image_only.pdf", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("image_only.pdf", fh, "application/pdf")},
        )
    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "PDF_NO_TEXT"
    assert body["message"]


def test_all_six_error_codes_have_distinct_messages():
    messages = set()

    empty = client.post(
        "/api/tokenize", data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"}
    ).json()
    messages.add(empty["message"])

    encoding = client.post(
        "/api/tokenize", data={"tokenizer_mode": "tiktoken", "text": "hi", "encoding": "bogus"}
    ).json()
    messages.add(encoding["message"])

    file_type = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
        files={"file": ("image.png", b"\x89PNG", "image/png")},
    ).json()
    messages.add(file_type["message"])

    with open(FIXTURES / "corrupted.pdf", "rb") as fh:
        invalid_pdf = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("corrupted.pdf", fh, "application/pdf")},
        ).json()
    messages.add(invalid_pdf["message"])

    with open(FIXTURES / "image_only.pdf", "rb") as fh:
        no_text = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("image_only.pdf", fh, "application/pdf")},
        ).json()
    messages.add(no_text["message"])

    # Every one of the 5 file/encoding-triggered messages is unique (FR-027, SC-005).
    assert len(messages) == 5
