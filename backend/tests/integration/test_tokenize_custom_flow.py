from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _tokenize_custom(text: str):
    response = client.post("/api/tokenize", data={"tokenizer_mode": "custom", "text": text})
    assert response.status_code == 200
    return response.json()


def test_same_input_twice_against_same_vocabulary_state_is_deterministic():
    first = _tokenize_custom("Hello, world!")
    second = _tokenize_custom("Hello, world!")

    first_ids = [t["id"] for t in first["tokens"]]
    second_ids = [t["id"] for t in second["tokens"]]
    assert first_ids == second_ids

    # Both runs are against the *same eventual* vocabulary state (all tokens
    # already existed after the first run), so the second run must not flag
    # anything as new.
    assert all(t["is_new"] is False for t in second["tokens"])


def test_overlapping_inputs_reuse_known_tokens_and_create_new_ones():
    first = _tokenize_custom("Hello, world!")
    assert all(t["is_new"] for t in first["tokens"])

    second = _tokenize_custom("Hello, again!")
    by_text = {t["text"]: t for t in second["tokens"]}

    assert by_text["Hello"]["is_new"] is False
    assert by_text["!"]["is_new"] is False
    assert by_text["again"]["is_new"] is True

    hello_id_first_run = next(t["id"] for t in first["tokens"] if t["text"] == "Hello")
    assert by_text["Hello"]["id"] == hello_id_first_run


def test_first_tokenize_on_empty_vocabulary_marks_every_token_new():
    result = _tokenize_custom("brand new text")
    assert all(t["is_new"] for t in result["tokens"])
