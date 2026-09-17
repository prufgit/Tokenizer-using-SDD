import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_full_tiktoken_tokenize_flow_matches_hand_computed_stats():
    text = "Hello, world! This is a test."

    response = client.post(
        "/api/tokenize",
        data={
            "tokenizer_mode": "tiktoken",
            "text": text,
            "encoding": "cl100k_base",
        },
    )

    assert response.status_code == 200
    body = response.json()

    token_count = len(body["tokens"])
    stats = body["stats"]

    assert stats["character_count"] == len(text)
    assert stats["word_count"] == len(text.split())
    assert stats["token_count"] == token_count
    assert stats["tokens_per_word"] == token_count / len(text.split())
    assert stats["tokens_per_character"] == token_count / len(text)

    # Reconstructing token text via offsets must reproduce the source text.
    reconstructed = "".join(t["text"] for t in body["tokens"])
    assert reconstructed == text


def test_switching_encoding_changes_token_ids():
    text = "Testing encoding switch behavior."

    first = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "text": text, "encoding": "cl100k_base"},
    ).json()
    second = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "text": text, "encoding": "o200k_base"},
    ).json()

    first_ids = [t["id"] for t in first["tokens"]]
    second_ids = [t["id"] for t in second["tokens"]]
    assert first_ids != second_ids


def test_tokenize_round_trip_completes_within_two_seconds_for_5000_characters():
    # SC-001: full tokenize-and-display round trip in under 2 seconds for inputs up
    # to 5,000 characters. Server-side processing time is the part this app controls
    # (network/render time is a frontend concern outside this test's scope).
    phrase = "The quick brown fox jumps over the lazy dog. "
    text = (phrase * (5000 // len(phrase) + 1))[:5000]
    assert len(text) == 5000

    start = time.perf_counter()
    response = client.post(
        "/api/tokenize",
        data={"tokenizer_mode": "tiktoken", "text": text, "encoding": "cl100k_base"},
    )
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2.0
