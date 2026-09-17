import pytest

from app.core.errors import (
    BpeModelNotTrainedError,
    BpeTargetVocabSizeInvalidError,
    BpeTrainingTextEmptyError,
    BpeTrainingTextTooLongError,
    BpeUnknownCharacterError,
)
from app.services import bpe_service
from app.services.bpe_model_store import BpeModelStore

CLASSIC_EXAMPLE = "aaabdaaabac"


# --- Training (T074) ---------------------------------------------------------


def test_first_merge_of_classic_example_is_the_most_frequent_pair():
    # "aaabdaaabac": bigram "aa" occurs 4 times, more than any other pair —
    # this is the well-known worked example for BPE.
    model = bpe_service.train(CLASSIC_EXAMPLE, target_vocab_size=10)

    assert model.merge_rules[0].left == "a"
    assert model.merge_rules[0].right == "a"
    assert model.merge_rules[0].merged == "aa"


def test_base_vocabulary_includes_every_distinct_character_including_space():
    model = bpe_service.train("ab ab", target_vocab_size=10)

    base_chars = {token for token in model.vocabulary if len(token) == 1}
    assert base_chars == {"a", "b", " "}


def test_training_is_deterministic_for_same_text_and_target_size():
    first = bpe_service.train(CLASSIC_EXAMPLE, target_vocab_size=10)
    second = bpe_service.train(CLASSIC_EXAMPLE, target_vocab_size=10)

    assert first.vocabulary == second.vocabulary
    assert [(r.left, r.right, r.merged) for r in first.merge_rules] == [
        (r.left, r.right, r.merged) for r in second.merge_rules
    ]


def test_training_stops_early_when_no_pair_repeats():
    # "abcdef" has no repeated adjacent pair at all — training must stop immediately
    # even though target_vocab_size asks for far more than the base alphabet.
    model = bpe_service.train("abcdef", target_vocab_size=50)

    assert model.achieved_vocab_size == 6
    assert model.achieved_vocab_size < model.target_vocab_size
    assert model.merge_rules == []


def test_training_stops_exactly_at_target_vocab_size():
    # "ab" repeated has one productive merge before hitting a small, exact target.
    model = bpe_service.train("abab", target_vocab_size=3)
    assert model.achieved_vocab_size == 3
    assert model.merge_rules[0].merged == "ab"


def test_classic_example_early_stops_below_a_larger_target():
    # After 3 productive merges (aa, aaa, aaab) the classic example has no repeated
    # adjacent pair left, so it stops short of a target_vocab_size of 9 (FR-040).
    model = bpe_service.train(CLASSIC_EXAMPLE, target_vocab_size=9)
    assert model.achieved_vocab_size == 7
    assert [r.merged for r in model.merge_rules] == ["aa", "aaa", "aaab"]


# --- Validation (T074) --------------------------------------------------------


def test_validate_training_text_rejects_empty():
    with pytest.raises(BpeTrainingTextEmptyError):
        bpe_service.validate_training_text("   ")


def test_validate_training_text_rejects_over_5000_characters():
    with pytest.raises(BpeTrainingTextTooLongError):
        bpe_service.validate_training_text("a" * 5001)


def test_validate_training_text_accepts_exactly_5000_characters():
    bpe_service.validate_training_text("a" * 5000)


def test_validate_target_vocab_size_rejects_non_positive():
    with pytest.raises(BpeTargetVocabSizeInvalidError):
        bpe_service.validate_target_vocab_size(0, "abc")


def test_validate_target_vocab_size_rejects_smaller_than_distinct_chars():
    with pytest.raises(BpeTargetVocabSizeInvalidError):
        bpe_service.validate_target_vocab_size(2, "abc")


def test_validate_target_vocab_size_rejects_over_500():
    with pytest.raises(BpeTargetVocabSizeInvalidError):
        bpe_service.validate_target_vocab_size(501, "abc")


def test_validate_target_vocab_size_accepts_500():
    bpe_service.validate_target_vocab_size(500, "abc")


# --- Tokenize-time merge application (T094) -----------------------------------


def _trained_store(text: str, target_vocab_size: int) -> BpeModelStore:
    store = BpeModelStore()
    store.replace(bpe_service.train(text, target_vocab_size))
    return store


def test_tokenize_applies_learned_merges_in_rank_order():
    store = _trained_store(CLASSIC_EXAMPLE, target_vocab_size=9)

    tokens = bpe_service.tokenize(CLASSIC_EXAMPLE, store)

    reconstructed = "".join(t.text for t in tokens)
    assert reconstructed == CLASSIC_EXAMPLE
    assert all(t.is_new is False for t in tokens)


def test_tokenize_is_deterministic_across_repeated_calls():
    store = _trained_store(CLASSIC_EXAMPLE, target_vocab_size=9)

    first = bpe_service.tokenize("aaab", store)
    second = bpe_service.tokenize("aaab", store)

    assert [(t.id, t.text) for t in first] == [(t.id, t.text) for t in second]


def test_tokenize_bytes_match_utf8_encoding_of_token_text():
    store = _trained_store(CLASSIC_EXAMPLE, target_vocab_size=9)

    tokens = bpe_service.tokenize("aaabac", store)

    for token in tokens:
        assert token.bytes == list(token.text.encode("utf-8"))


def test_tokenize_offsets_cover_the_full_source_text():
    store = _trained_store(CLASSIC_EXAMPLE, target_vocab_size=9)
    text = "aaabac"

    tokens = bpe_service.tokenize(text, store)

    assert tokens[0].start == 0
    assert tokens[-1].end == len(text)
    for token in tokens:
        assert text[token.start : token.end] == token.text


def test_tokenize_rejects_unseen_character():
    store = _trained_store(CLASSIC_EXAMPLE, target_vocab_size=9)

    with pytest.raises(BpeUnknownCharacterError):
        bpe_service.tokenize("xyz", store)


def test_tokenize_rejects_when_no_model_trained():
    store = BpeModelStore()

    with pytest.raises(BpeModelNotTrainedError):
        bpe_service.tokenize("abc", store)
