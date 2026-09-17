import pytest

from app.services.bpe_model_store import bpe_model_store
from app.services.vocabulary_store import vocabulary_store


@pytest.fixture(autouse=True)
def reset_vocabulary_store():
    """Isolate tests from each other's Custom Tokenizer vocabulary state."""
    vocabulary_store.reset()
    yield
    vocabulary_store.reset()


@pytest.fixture(autouse=True)
def reset_bpe_model_store():
    """Isolate tests from each other's trained BPE model state."""
    bpe_model_store.reset()
    yield
    bpe_model_store.reset()
