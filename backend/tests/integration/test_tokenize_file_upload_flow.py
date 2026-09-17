from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_txt_upload_matches_typing_the_same_text():
    typed_text = FIXTURES.joinpath("sample.txt").read_text(encoding="utf-8")

    typed_response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "text": typed_text, "encoding": "cl100k_base"},
    ).json()

    with open(FIXTURES / "sample.txt", "rb") as fh:
        upload_response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("sample.txt", fh, "text/plain")},
        ).json()

    assert [t["id"] for t in upload_response["tokens"]] == [t["id"] for t in typed_response["tokens"]]
    assert upload_response["stats"] == typed_response["stats"]


def test_pdf_upload_extracts_and_tokenizes_embedded_text():
    with open(FIXTURES / "sample_text.pdf", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("sample_text.pdf", fh, "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    reconstructed = "".join(t["text"] for t in body["tokens"])
    assert "Hello from a PDF" in reconstructed


def test_password_protected_pdf_upload_returns_invalid_pdf_error():
    with open(FIXTURES / "password_protected.pdf", "rb") as fh:
        response = client.post(
            "/api/tokenize",
            data={"tokenizer_mode": "tiktoken", "encoding": "cl100k_base"},
            files={"file": ("password_protected.pdf", fh, "application/pdf")},
        )

    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_PDF"
