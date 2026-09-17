from pydantic import BaseModel


class BpeTrainRequest(BaseModel):
    training_text: str
    target_vocab_size: int


class BpeVocabularyEntry(BaseModel):
    id: int
    token: str


class BpeMergeRule(BaseModel):
    order: int
    left: str
    right: str
    merged: str
    merged_id: int


class BpeTrainingStep(BaseModel):
    step: int
    pair_selected: tuple[str, str]
    merged_into: str


class BpeModelResponse(BaseModel):
    trained: bool
    vocabulary: list[BpeVocabularyEntry]
    merge_rules: list[BpeMergeRule]
    training_steps: list[BpeTrainingStep]
    target_vocab_size: int | None
    achieved_vocab_size: int | None
