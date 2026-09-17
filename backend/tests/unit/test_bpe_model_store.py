from app.services.bpe_model_store import BpeModel, BpeModelStore, MergeRule, TrainingStep


def test_initial_store_is_untrained():
    store = BpeModelStore()
    assert store.current().trained is False


def test_replace_marks_model_trained():
    store = BpeModelStore()
    model = BpeModel(
        vocabulary={"a": 0, "b": 1, "ab": 2},
        merge_rules=[MergeRule(order=0, left="a", right="b", merged="ab", merged_id=2)],
        training_steps=[TrainingStep(step=0, pair_selected=("a", "b"), merged_into="ab")],
        target_vocab_size=3,
        achieved_vocab_size=3,
    )

    store.replace(model)

    current = store.current()
    assert current.trained is True
    assert current.vocabulary == {"a": 0, "b": 1, "ab": 2}
    assert current.achieved_vocab_size == 3


def test_second_training_run_fully_replaces_first():
    store = BpeModelStore()
    store.replace(
        BpeModel(vocabulary={"x": 0}, achieved_vocab_size=1, target_vocab_size=1)
    )
    store.replace(
        BpeModel(vocabulary={"y": 0, "z": 1}, achieved_vocab_size=2, target_vocab_size=2)
    )

    current = store.current()
    assert current.vocabulary == {"y": 0, "z": 1}
    assert "x" not in current.vocabulary


def test_reset_returns_store_to_untrained():
    store = BpeModelStore()
    store.replace(BpeModel(vocabulary={"x": 0}, achieved_vocab_size=1, target_vocab_size=1))

    store.reset()

    assert store.current().trained is False
    assert store.current().vocabulary == {}
