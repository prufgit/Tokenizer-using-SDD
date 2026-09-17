from app.services.statistics import compute_statistics


def test_computes_character_word_token_counts():
    stats = compute_statistics("Hello, world!", token_count=4)

    assert stats.character_count == 13
    assert stats.word_count == 2
    assert stats.token_count == 4


def test_computes_ratios_for_non_empty_text():
    stats = compute_statistics("Hello, world!", token_count=4)

    assert stats.tokens_per_word == 4 / 2
    assert stats.tokens_per_character == 4 / 13


def test_tokens_per_word_is_zero_when_word_count_is_zero():
    # No text reaches compute_statistics with word_count == 0 via the API today
    # (EMPTY_INPUT is rejected first), but the guard itself must still be correct.
    stats = compute_statistics("   ", token_count=0)

    assert stats.word_count == 0
    assert stats.tokens_per_word == 0.0


def test_tokens_per_character_is_zero_when_character_count_is_zero():
    stats = compute_statistics("", token_count=0)

    assert stats.character_count == 0
    assert stats.tokens_per_character == 0.0


def test_single_word_single_character_counts():
    stats = compute_statistics("a", token_count=1)

    assert stats.character_count == 1
    assert stats.word_count == 1
    assert stats.tokens_per_word == 1.0
    assert stats.tokens_per_character == 1.0
