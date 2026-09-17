from app.core.config import settings
from app.core.errors import (
    BpeModelNotTrainedError,
    BpeTargetVocabSizeInvalidError,
    BpeTrainingTextEmptyError,
    BpeTrainingTextTooLongError,
    BpeUnknownCharacterError,
)
from app.schemas.tokenize import Token
from app.services.bpe_model_store import BpeModel, BpeModelStore, MergeRule, TrainingStep


def validate_training_text(training_text: str) -> str:
    if not training_text.strip():
        raise BpeTrainingTextEmptyError(
            "Please enter some training text to train the BPE tokenizer."
        )
    if len(training_text) > settings.bpe_max_training_text_length:
        raise BpeTrainingTextTooLongError(
            "Training text is too long. The maximum length is "
            f"{settings.bpe_max_training_text_length} characters."
        )
    return training_text


def validate_target_vocab_size(target_vocab_size: int, training_text: str) -> int:
    distinct_chars = len(set(training_text))
    if target_vocab_size <= 0:
        raise BpeTargetVocabSizeInvalidError(
            "Target vocabulary size must be a positive number."
        )
    if target_vocab_size < distinct_chars:
        raise BpeTargetVocabSizeInvalidError(
            f"Target vocabulary size must be at least {distinct_chars} (the number "
            "of distinct characters, including whitespace, in the training text)."
        )
    if target_vocab_size > settings.bpe_max_target_vocab_size:
        raise BpeTargetVocabSizeInvalidError(
            f"Target vocabulary size must be at most {settings.bpe_max_target_vocab_size}."
        )
    return target_vocab_size


def _get_or_create_id(vocabulary: dict[str, int], token: str) -> int:
    existing = vocabulary.get(token)
    if existing is not None:
        return existing
    new_id = len(vocabulary)
    vocabulary[token] = new_id
    return new_id


def _apply_merge_once(symbols: list[str], left: str, right: str, merged: str) -> list[str]:
    result: list[str] = []
    i = 0
    while i < len(symbols):
        if i < len(symbols) - 1 and symbols[i] == left and symbols[i + 1] == right:
            result.append(merged)
            i += 2
        else:
            result.append(symbols[i])
            i += 1
    return result


def train(training_text: str, target_vocab_size: int) -> BpeModel:
    """Learn a BPE vocabulary and ordered merge rules (FR-035-FR-037).

    Whitespace is an ordinary character in one continuous stream (no
    pre-tokenization, per Clarifications). Ties in pair frequency are broken by
    leftmost first occurrence — a natural consequence of scanning left-to-right into
    an insertion-ordered dict and picking the first `max()` (research.md decision 10).
    """
    validate_training_text(training_text)
    validate_target_vocab_size(target_vocab_size, training_text)

    symbols = list(training_text)
    vocabulary: dict[str, int] = {}
    for char in symbols:
        _get_or_create_id(vocabulary, char)

    merge_rules: list[MergeRule] = []
    training_steps: list[TrainingStep] = []

    while len(vocabulary) < target_vocab_size:
        pair_counts: dict[tuple[str, str], int] = {}
        for left, right in zip(symbols, symbols[1:]):
            pair = (left, right)
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

        if not pair_counts:
            break

        best_pair = max(pair_counts, key=pair_counts.get)
        if pair_counts[best_pair] <= 1:
            break  # No pair repeats — further merges wouldn't be useful (FR-040)

        left, right = best_pair
        merged = left + right
        merged_id = _get_or_create_id(vocabulary, merged)

        step = len(merge_rules)
        merge_rules.append(
            MergeRule(order=step, left=left, right=right, merged=merged, merged_id=merged_id)
        )
        training_steps.append(
            TrainingStep(step=step, pair_selected=(left, right), merged_into=merged)
        )

        symbols = _apply_merge_once(symbols, left, right, merged)

    return BpeModel(
        vocabulary=vocabulary,
        merge_rules=merge_rules,
        training_steps=training_steps,
        target_vocab_size=target_vocab_size,
        achieved_vocab_size=len(vocabulary),
    )


def require_trained_model(store: BpeModelStore) -> BpeModel:
    model = store.current()
    if not model.trained:
        raise BpeModelNotTrainedError(
            "No BPE model has been trained yet. Train one first, then try again."
        )
    return model


def require_known_characters(text: str, model: BpeModel) -> None:
    base_characters = {token for token in model.vocabulary if len(token) == 1}
    for char in text:
        if char not in base_characters:
            raise BpeUnknownCharacterError(
                f"This text contains a character not seen during training: {char!r}."
            )


def tokenize(text: str, store: BpeModelStore) -> list[Token]:
    """Apply only the learned merge rules, in learned order (FR-047).

    Repeatedly finds the lowest-rank (earliest-learned) merge rule whose pair still
    occurs adjacently anywhere in the current symbol list, and applies every
    non-overlapping occurrence of it, until no learned rule's pair remains
    (research.md decision 12). Never creates a new rule.
    """
    model = require_trained_model(store)
    require_known_characters(text, model)

    rank_of_pair = {(rule.left, rule.right): rule.order for rule in model.merge_rules}

    symbols: list[str] = list(text)
    starts: list[int] = list(range(len(text)))
    ends: list[int] = [i + 1 for i in range(len(text))]

    while True:
        best_rank: int | None = None
        best_index = -1
        for i in range(len(symbols) - 1):
            rank = rank_of_pair.get((symbols[i], symbols[i + 1]))
            if rank is not None and (best_rank is None or rank < best_rank):
                best_rank = rank
                best_index = i

        if best_rank is None:
            break

        left, right = symbols[best_index], symbols[best_index + 1]
        merged = left + right

        new_symbols: list[str] = []
        new_starts: list[int] = []
        new_ends: list[int] = []
        i = 0
        while i < len(symbols):
            if i < len(symbols) - 1 and symbols[i] == left and symbols[i + 1] == right:
                new_symbols.append(merged)
                new_starts.append(starts[i])
                new_ends.append(ends[i + 1])
                i += 2
            else:
                new_symbols.append(symbols[i])
                new_starts.append(starts[i])
                new_ends.append(ends[i])
                i += 1
        symbols, starts, ends = new_symbols, new_starts, new_ends

    return [
        Token(
            index=index,
            id=model.vocabulary[symbol],
            text=symbol,
            start=starts[index],
            end=ends[index],
            is_new=False,
        )
        for index, symbol in enumerate(symbols)
    ]
