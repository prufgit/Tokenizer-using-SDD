from app.services.vocabulary_store import VocabularyStore


def test_new_token_gets_sequential_deterministic_id():
    store = VocabularyStore()

    first_id = store.get_or_create_id("alpha")
    second_id = store.get_or_create_id("beta")

    assert first_id == 0
    assert second_id == 1


def test_existing_token_reuses_its_id():
    store = VocabularyStore()
    first_id = store.get_or_create_id("alpha")

    assert store.get_or_create_id("alpha") == first_id


def test_frequency_accumulates_across_multiple_operations():
    store = VocabularyStore()
    store.get_or_create_id("alpha")
    store.record_occurrence("alpha")
    store.get_or_create_id("alpha")
    store.record_occurrence("alpha")

    assert store.frequency["alpha"] == 2


def test_reset_clears_vocabulary_and_restarts_id_assignment():
    store = VocabularyStore()
    store.get_or_create_id("alpha")
    store.get_or_create_id("beta")

    store.reset()

    assert store.token_to_id == {}
    assert store.frequency == {}
    assert store.get_or_create_id("gamma") == 0


def test_entries_reflect_current_vocabulary_state():
    store = VocabularyStore()
    store.get_or_create_id("alpha")
    store.record_occurrence("alpha")

    entries = store.entries()

    assert len(entries) == 1
    assert entries[0].id == 0
    assert entries[0].token == "alpha"
    assert entries[0].frequency == 1
