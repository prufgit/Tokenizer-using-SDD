from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_train_then_view_then_retrain_replaces_previous_model():
    # 1. Train.
    train_response = client.post(
        "/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9}
    )
    assert train_response.status_code == 200
    trained_body = train_response.json()

    # 2. GET /api/bpe/model immediately reflects it.
    model_response = client.get("/api/bpe/model")
    assert model_response.status_code == 200
    assert model_response.json() == trained_body

    # 3. Train again with different text — previous model is fully replaced.
    second_response = client.post(
        "/api/bpe/train", json={"training_text": "xyzxyzxyz", "target_vocab_size": 5}
    )
    assert second_response.status_code == 200
    second_body = second_response.json()

    second_tokens = {entry["token"] for entry in second_body["vocabulary"]}
    assert "a" not in second_tokens  # nothing from the first training run survives

    model_after_retrain = client.get("/api/bpe/model").json()
    assert model_after_retrain == second_body


def test_training_with_identical_input_twice_produces_identical_model():
    first = client.post(
        "/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9}
    ).json()
    second = client.post(
        "/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9}
    ).json()

    assert first["vocabulary"] == second["vocabulary"]
    assert first["merge_rules"] == second["merge_rules"]
