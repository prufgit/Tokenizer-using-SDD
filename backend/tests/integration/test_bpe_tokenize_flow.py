from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _train():
    return client.post(
        "/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9}
    ).json()


def test_tokenize_before_training_is_rejected():
    response = client.post("/api/tokenize", data={"tokenizer_mode": "bpe", "text": "aaab"})
    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_MODEL_NOT_TRAINED"


def test_train_then_tokenize_uses_learned_vocabulary():
    trained = _train()
    trained_ids = {entry["token"]: entry["id"] for entry in trained["vocabulary"]}

    response = client.post("/api/tokenize", data={"tokenizer_mode": "bpe", "text": "aaab"})
    assert response.status_code == 200
    body = response.json()

    for token in body["tokens"]:
        assert trained_ids[token["text"]] == token["id"]


def test_tokenize_same_text_twice_is_deterministic():
    _train()

    first = client.post("/api/tokenize", data={"tokenizer_mode": "bpe", "text": "aaabac"}).json()
    second = client.post("/api/tokenize", data={"tokenizer_mode": "bpe", "text": "aaabac"}).json()

    assert [t["id"] for t in first["tokens"]] == [t["id"] for t in second["tokens"]]


def test_tokenize_rejects_unseen_character():
    _train()

    response = client.post("/api/tokenize", data={"tokenizer_mode": "bpe", "text": "hello"})
    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_UNKNOWN_CHARACTER"


def test_tokenize_after_reset_via_retrain_is_rejected_for_stale_expectations():
    _train()
    # Retraining on different text changes the base vocabulary — old characters may
    # no longer be recognized if they don't appear in the new training text.
    client.post("/api/bpe/train", json={"training_text": "xyz", "target_vocab_size": 3})

    response = client.post("/api/tokenize", data={"tokenizer_mode": "bpe", "text": "aaab"})
    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_UNKNOWN_CHARACTER"
