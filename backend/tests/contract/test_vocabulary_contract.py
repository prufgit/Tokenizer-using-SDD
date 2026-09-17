from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_vocabulary_empty_shape():
    response = client.get("/api/vocabulary")
    assert response.status_code == 200
    assert response.json() == {"entries": [], "total_entries": 0}


def test_get_vocabulary_after_tokenize_lists_entries():
    client.post("/api/tokenize", data={"tokenizer_mode": "custom", "text": "hi there"})

    response = client.get("/api/vocabulary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_entries"] == 2
    for entry in body["entries"]:
        assert set(entry.keys()) == {"id", "token", "frequency", "status"}
        assert entry["status"] in ("new", "existing")


def test_reset_vocabulary_returns_to_empty_shape():
    client.post("/api/tokenize", data={"tokenizer_mode": "custom", "text": "hi there"})

    response = client.post("/api/vocabulary/reset")
    assert response.status_code == 200
    assert response.json() == {"entries": [], "total_entries": 0}


def test_reset_vocabulary_is_idempotent_on_already_empty_vocabulary():
    response = client.post("/api/vocabulary/reset")
    assert response.status_code == 200
    assert response.json() == {"entries": [], "total_entries": 0}
