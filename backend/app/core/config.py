from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TOKENIZER_")

    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB, per spec Clarifications
    allowed_cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # BPE amendment (per spec Clarifications)
    bpe_max_training_text_length: int = 5000
    bpe_max_target_vocab_size: int = 500


settings = Settings()
