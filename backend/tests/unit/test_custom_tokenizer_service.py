from app.services.custom_tokenizer_service import tokenize
from app.services.vocabulary_store import VocabularyStore


def test_splits_words_and_punctuation_as_separate_tokens():
    store = VocabularyStore()
    tokens = tokenize("Hello, world!", store)

    texts = [t.text for t in tokens]
    assert texts == ["Hello", ",", "world", "!"]


def test_offsets_match_exact_positions_in_source_text():
    text = "Hello, world!"
    store = VocabularyStore()
    tokens = tokenize(text, store)

    for token in tokens:
        assert text[token.start : token.end] == token.text


def test_no_whitespace_tokens_are_emitted():
    store = VocabularyStore()
    tokens = tokenize("a   b\tc\nd", store)
    assert all(not t.text.isspace() for t in tokens)
    assert [t.text for t in tokens] == ["a", "b", "c", "d"]


def test_first_sighting_of_every_token_is_marked_new():
    store = VocabularyStore()
    tokens = tokenize("Hello, world!", store)
    assert all(t.is_new for t in tokens)


def test_repeated_token_reuses_id_and_is_not_new():
    store = VocabularyStore()
    first = tokenize("Hello, world!", store)
    second = tokenize("Hello, again!", store)

    hello_first = next(t for t in first if t.text == "Hello")
    hello_second = next(t for t in second if t.text == "Hello")

    assert hello_second.id == hello_first.id
    assert hello_second.is_new is False


def test_token_repeated_within_one_operation_is_created_once_and_marked_new_once():
    store = VocabularyStore()
    tokens = tokenize("go go go", store)

    go_tokens = [t for t in tokens if t.text == "go"]
    assert len(go_tokens) == 3
    assert all(t.id == go_tokens[0].id for t in go_tokens)
    assert all(t.is_new for t in go_tokens)
    assert store.frequency["go"] == 3
