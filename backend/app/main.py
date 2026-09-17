from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import bpe, encodings, tokenize, vocabulary
from app.core.config import settings
from app.core.errors import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Tokenizer API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(tokenize.router)
    app.include_router(encodings.router)
    app.include_router(vocabulary.router)
    app.include_router(bpe.router)

    return app


app = create_app()
