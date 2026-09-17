import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class VocabularyEntry:
    id: int
    token: str
    frequency: int


class VocabularyStore:
    """Single in-memory Custom Tokenizer vocabulary (Constitution Principle VI).

    IDs are assigned by a monotonically increasing counter starting at 0, so a
    given unseen token always gets the same next ID for a given vocabulary state
    (FR-014). Guarded by a lock since FastAPI may serve concurrent requests.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.token_to_id: dict[str, int] = {}
        self.frequency: dict[str, int] = {}
        self.next_id: int = 0
        self.last_new_tokens: set[str] = set()

    def get_or_create_id(self, token: str) -> int:
        with self._lock:
            existing = self.token_to_id.get(token)
            if existing is not None:
                return existing
            new_id = self.next_id
            self.token_to_id[token] = new_id
            self.frequency[token] = 0
            self.next_id += 1
            return new_id

    def record_occurrence(self, token: str) -> None:
        with self._lock:
            self.frequency[token] = self.frequency.get(token, 0) + 1

    def reset(self) -> None:
        with self._lock:
            self.token_to_id.clear()
            self.frequency.clear()
            self.next_id = 0
            self.last_new_tokens.clear()

    def entries(self) -> list[VocabularyEntry]:
        with self._lock:
            return [
                VocabularyEntry(id=token_id, token=token, frequency=self.frequency[token])
                for token, token_id in sorted(self.token_to_id.items(), key=lambda kv: kv[1])
            ]


vocabulary_store = VocabularyStore()
