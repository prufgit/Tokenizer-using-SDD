import threading
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MergeRule:
    order: int
    left: str
    right: str
    merged: str
    merged_id: int


@dataclass(frozen=True)
class TrainingStep:
    step: int
    pair_selected: tuple[str, str]
    merged_into: str


@dataclass
class BpeModel:
    vocabulary: dict[str, int] = field(default_factory=dict)
    merge_rules: list[MergeRule] = field(default_factory=list)
    training_steps: list[TrainingStep] = field(default_factory=list)
    target_vocab_size: int | None = None
    achieved_vocab_size: int | None = None

    @property
    def trained(self) -> bool:
        return self.achieved_vocab_size is not None


class BpeModelStore:
    """Single in-memory trained BPE model (Constitution Principle VI).

    Fully independent of the Simple strategy's VocabularyStore — a new successful
    training run atomically replaces the entire previous model (FR-041), never merges
    with it.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._model = BpeModel()

    def replace(self, model: BpeModel) -> None:
        with self._lock:
            self._model = model

    def current(self) -> BpeModel:
        with self._lock:
            return self._model

    def reset(self) -> None:
        with self._lock:
            self._model = BpeModel()


bpe_model_store = BpeModelStore()
