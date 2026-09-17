from pydantic import BaseModel


class EncodingsResponse(BaseModel):
    encodings: list[str]
