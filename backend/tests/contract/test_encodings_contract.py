from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_encodings_returns_non_empty_list():
    response = client.get("/api/encodings")

    assert response.status_code == 200
    body = response.json()
    assert "encodings" in body
    assert isinstance(body["encodings"], list)
    assert len(body["encodings"]) > 0
    assert "cl100k_base" in body["encodings"]
