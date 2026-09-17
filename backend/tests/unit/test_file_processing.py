from pathlib import Path

import pytest

from app.core.errors import (
    FileTooLargeError,
    InvalidPdfError,
    PdfNoTextError,
    UnsupportedFileTypeError,
)
from app.services.file_processing import (
    MAX_UPLOAD_SIZE_BYTES,
    extract_pdf_text,
    extract_txt_text,
    validate_file_type,
    validate_file_size,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_extract_txt_text_decodes_utf8_bytes():
    content = FIXTURES.joinpath("sample.txt").read_bytes()
    assert "Hello from a TXT file" in extract_txt_text(content)


def test_extract_pdf_text_returns_embedded_text():
    content = FIXTURES.joinpath("sample_text.pdf").read_bytes()
    text = extract_pdf_text(content)
    assert "Hello from a PDF" in text


def test_extract_pdf_text_raises_invalid_pdf_for_corrupted_file():
    content = FIXTURES.joinpath("corrupted.pdf").read_bytes()
    with pytest.raises(InvalidPdfError):
        extract_pdf_text(content)


def test_extract_pdf_text_raises_invalid_pdf_for_password_protected_file():
    content = FIXTURES.joinpath("password_protected.pdf").read_bytes()
    with pytest.raises(InvalidPdfError):
        extract_pdf_text(content)


def test_extract_pdf_text_raises_pdf_no_text_for_image_only_file():
    content = FIXTURES.joinpath("image_only.pdf").read_bytes()
    with pytest.raises(PdfNoTextError):
        extract_pdf_text(content)


def test_validate_file_type_accepts_txt_and_pdf():
    validate_file_type("notes.txt", "text/plain")
    validate_file_type("doc.pdf", "application/pdf")


def test_validate_file_type_rejects_other_types():
    with pytest.raises(UnsupportedFileTypeError):
        validate_file_type("image.png", "image/png")


def test_validate_file_size_accepts_under_limit():
    validate_file_size(1024)


def test_validate_file_size_rejects_over_limit():
    with pytest.raises(FileTooLargeError):
        validate_file_size(MAX_UPLOAD_SIZE_BYTES + 1)
