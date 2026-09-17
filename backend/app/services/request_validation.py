from fastapi import HTTPException, UploadFile

from app.core.errors import EmptyInputError


def resolve_input_text_field(
    text: str | None, file: UploadFile | None
) -> tuple[str | None, UploadFile | None]:
    """Enforce "exactly one of text/file" (FR-021, contracts/tokenize-endpoint.md).

    Returns the pair unchanged when exactly one is meaningfully present. Blank/
    whitespace-only `text` is treated as absent so a file can still be used.
    """
    has_text = text is not None and text.strip() != ""
    has_file = file is not None and file.filename not in (None, "")

    if has_text and has_file:
        raise HTTPException(
            status_code=400,
            detail="Provide either text or a file, not both.",
        )
    if not has_text and not has_file:
        raise EmptyInputError("Please enter some text or upload a file to tokenize.")

    return (text if has_text else None), (file if has_file else None)


def require_non_empty_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        raise EmptyInputError("Please enter some text or upload a file to tokenize.")
    return text
