from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schemas.errors import ErrorCode, ErrorResponse


class TokenizerAppError(Exception):
    """Base for domain errors that map to a client-facing ErrorResponse (FR-027)."""

    error_code: ErrorCode
    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EmptyInputError(TokenizerAppError):
    error_code = ErrorCode.EMPTY_INPUT


class UnsupportedFileTypeError(TokenizerAppError):
    error_code = ErrorCode.UNSUPPORTED_FILE_TYPE


class FileTooLargeError(TokenizerAppError):
    error_code = ErrorCode.FILE_TOO_LARGE


class InvalidPdfError(TokenizerAppError):
    error_code = ErrorCode.INVALID_PDF


class PdfNoTextError(TokenizerAppError):
    error_code = ErrorCode.PDF_NO_TEXT


class UnsupportedEncodingError(TokenizerAppError):
    error_code = ErrorCode.UNSUPPORTED_ENCODING


class BpeTrainingTextEmptyError(TokenizerAppError):
    error_code = ErrorCode.BPE_TRAINING_TEXT_EMPTY


class BpeTrainingTextTooLongError(TokenizerAppError):
    error_code = ErrorCode.BPE_TRAINING_TEXT_TOO_LONG


class BpeTargetVocabSizeInvalidError(TokenizerAppError):
    error_code = ErrorCode.BPE_TARGET_VOCAB_SIZE_INVALID


class BpeModelNotTrainedError(TokenizerAppError):
    error_code = ErrorCode.BPE_MODEL_NOT_TRAINED


class BpeUnknownCharacterError(TokenizerAppError):
    error_code = ErrorCode.BPE_UNKNOWN_CHARACTER


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TokenizerAppError)
    async def handle_tokenizer_app_error(
        request: Request, exc: TokenizerAppError
    ) -> JSONResponse:
        body = ErrorResponse(error_code=exc.error_code, message=exc.message)
        return JSONResponse(status_code=400, content=body.model_dump())
