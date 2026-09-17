import fitz

from app.core.config import settings
from app.core.errors import (
    FileTooLargeError,
    InvalidPdfError,
    PdfNoTextError,
    UnsupportedFileTypeError,
)

MAX_UPLOAD_SIZE_BYTES = settings.max_upload_size_bytes

_TXT_EXTENSIONS = (".txt",)
_PDF_EXTENSIONS = (".pdf",)
_TXT_CONTENT_TYPES = {"text/plain"}
_PDF_CONTENT_TYPES = {"application/pdf"}


def validate_file_type(filename: str, content_type: str | None) -> None:
    lower_name = filename.lower()
    is_txt = lower_name.endswith(_TXT_EXTENSIONS) or content_type in _TXT_CONTENT_TYPES
    is_pdf = lower_name.endswith(_PDF_EXTENSIONS) or content_type in _PDF_CONTENT_TYPES
    if not (is_txt or is_pdf):
        raise UnsupportedFileTypeError(
            "Only TXT and PDF files are supported. Please upload a .txt or .pdf file."
        )


def validate_file_size(size_bytes: int) -> None:
    if size_bytes > MAX_UPLOAD_SIZE_BYTES:
        limit_mb = MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        raise FileTooLargeError(f"File is too large. The maximum allowed size is {limit_mb} MB.")


def extract_txt_text(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise UnsupportedFileTypeError(
            "This file doesn't look like a valid UTF-8 text file."
        ) from exc


def extract_pdf_text(content: bytes) -> str:
    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:  # PyMuPDF raises its own FileDataError/RuntimeError variants
        raise InvalidPdfError(
            "This PDF is invalid or corrupted and could not be opened."
        ) from exc

    with document:
        if document.needs_pass:
            raise InvalidPdfError(
                "This PDF is password-protected and could not be opened."
            )

        text = "\n".join(page.get_text() for page in document)

    if not text.strip():
        raise PdfNoTextError(
            "This PDF doesn't contain any extractable text (it may be a scanned "
            "image). Try a text-based PDF or a TXT file instead."
        )

    return text


def is_pdf(filename: str, content_type: str | None) -> bool:
    return filename.lower().endswith(_PDF_EXTENSIONS) or content_type in _PDF_CONTENT_TYPES


def extract_text(filename: str, content_type: str | None, content: bytes) -> str:
    validate_file_type(filename, content_type)
    validate_file_size(len(content))

    if is_pdf(filename, content_type):
        return extract_pdf_text(content)
    return extract_txt_text(content)
