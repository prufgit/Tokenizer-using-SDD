from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_bpe_model_untrained_shape():
    response = client.get("/api/bpe/model")

    assert response.status_code == 200
    assert response.json() == {
        "trained": False,
        "vocabulary": [],
        "merge_rules": [],
        "training_steps": [],
        "target_vocab_size": None,
        "achieved_vocab_size": None,
    }


def test_post_bpe_train_success_shape():
    response = client.post(
        "/api/bpe/train",
        json={"training_text": "aaabdaaabac", "target_vocab_size": 9},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trained"] is True
    assert len(body["vocabulary"]) == 7
    assert len(body["merge_rules"]) == 3
    assert len(body["training_steps"]) == 3
    assert body["target_vocab_size"] == 9
    assert body["achieved_vocab_size"] == 7

    for entry in body["vocabulary"]:
        assert set(entry.keys()) == {"id", "token"}
    for rule in body["merge_rules"]:
        assert set(rule.keys()) == {"order", "left", "right", "merged", "merged_id"}
    for step in body["training_steps"]:
        assert set(step.keys()) == {"step", "pair_selected", "merged_into"}


def test_get_bpe_model_reflects_last_training_run():
    client.post("/api/bpe/train", json={"training_text": "aaabdaaabac", "target_vocab_size": 9})

    response = client.get("/api/bpe/model")

    assert response.status_code == 200
    assert response.json()["trained"] is True
    assert response.json()["achieved_vocab_size"] == 7


def test_post_bpe_train_empty_text_returns_error():
    response = client.post("/api/bpe/train", json={"training_text": "   ", "target_vocab_size": 5})

    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_TRAINING_TEXT_EMPTY"


def test_post_bpe_train_text_too_long_returns_error():
    response = client.post(
        "/api/bpe/train", json={"training_text": "a" * 5001, "target_vocab_size": 5}
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_TRAINING_TEXT_TOO_LONG"


def test_post_bpe_train_invalid_target_vocab_size_returns_error():
    response = client.post(
        "/api/bpe/train", json={"training_text": "abc", "target_vocab_size": 0}
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_TARGET_VOCAB_SIZE_INVALID"


def test_post_bpe_train_target_vocab_size_over_500_returns_error():
    response = client.post(
        "/api/bpe/train", json={"training_text": "abc", "target_vocab_size": 501}
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "BPE_TARGET_VOCAB_SIZE_INVALID"
