from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_vocabulary_lifecycle_populate_view_reset_repopulate():
    # 1. Populate via a custom tokenize.
    first = client.post(
        "/api/tokenize", data={"tokenizer_mode": "custom", "text": "Hello, world!"}
    ).json()
    assert all(t["is_new"] for t in first["tokens"])

    # 2. View: every entry present, status "new" (all created in that last op).
    vocab = client.get("/api/vocabulary").json()
    assert vocab["total_entries"] == 4  # Hello , world !
    assert all(e["status"] == "new" for e in vocab["entries"])

    # A second, different custom tokenize changes which entries are "new".
    client.post("/api/tokenize", data={"tokenizer_mode": "custom", "text": "Hello, again!"})
    vocab_after_second = client.get("/api/vocabulary").json()
    by_token = {e["token"]: e for e in vocab_after_second["entries"]}
    assert by_token["Hello"]["status"] == "existing"
    assert by_token["again"]["status"] == "new"

    # 3. Reset clears everything.
    reset_body = client.post("/api/vocabulary/reset").json()
    assert reset_body == {"entries": [], "total_entries": 0}
    assert client.get("/api/vocabulary").json() == {"entries": [], "total_entries": 0}

    # 4. Re-tokenizing the same text is "new" again since vocabulary was cleared.
    repeat = client.post(
        "/api/tokenize", data={"tokenizer_mode": "custom", "text": "Hello, world!"}
    ).json()
    assert all(t["is_new"] for t in repeat["tokens"])
