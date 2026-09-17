from fastapi import APIRouter, Form, UploadFile

from app.services import (
    bpe_service,
    custom_tokenizer_service,
    file_processing,
    request_validation,
    statistics,
    tiktoken_service,
)
from app.services.bpe_model_store import bpe_model_store
from app.services.vocabulary_store import vocabulary_store
from app.schemas.tokenize import TokenizeResponse

router = APIRouter()


@router.post("/api/tokenize", response_model=TokenizeResponse)
async def post_tokenize(
    tokenizer_mode: str = Form(...),
    text: str | None = Form(None),
    encoding: str | None = Form(None),
    file: UploadFile | None = None,
) -> TokenizeResponse:
    resolved_text, resolved_file = request_validation.resolve_input_text_field(
        text, file
    )

    if resolved_file is not None:
        source_text = await _extract_file_text(resolved_file)
    else:
        source_text = resolved_text or ""

    # Applies to both typed text and file-extracted text: whitespace-only
    # content (e.g. a TXT file containing only spaces) is EMPTY_INPUT (FR-021).
    source_text = request_validation.require_non_empty_text(source_text)

    if tokenizer_mode == "tiktoken":
        encoding_name = tiktoken_service.require_supported_encoding(encoding)
        tokens = tiktoken_service.tokenize(source_text, encoding_name)
        stats = statistics.compute_statistics(source_text, len(tokens))
        return TokenizeResponse(
            tokenizer_mode="tiktoken",
            encoding=encoding_name,
            tokens=tokens,
            stats=stats,
        )

    if tokenizer_mode == "bpe":
        tokens = bpe_service.tokenize(source_text, bpe_model_store)
        stats = statistics.compute_statistics(source_text, len(tokens))
        return TokenizeResponse(
            tokenizer_mode="bpe",
            encoding=None,
            tokens=tokens,
            stats=stats,
        )

    tokens = custom_tokenizer_service.tokenize(source_text, vocabulary_store)
    stats = statistics.compute_statistics(source_text, len(tokens))
    return TokenizeResponse(
        tokenizer_mode="custom",
        encoding=None,
        tokens=tokens,
        stats=stats,
    )


async def _extract_file_text(file: UploadFile) -> str:
    content = await file.read()
    return file_processing.extract_text(file.filename or "", file.content_type, content)
