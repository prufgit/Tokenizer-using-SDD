export type TokenizerMode = "tiktoken" | "custom" | "bpe";

export type CustomStrategy = "simple" | "bpe";

export interface Token {
  index: number;
  id: number;
  text: string;
  start: number;
  end: number;
  is_new: boolean | null;
  bytes: number[];
}

export interface Statistics {
  character_count: number;
  word_count: number;
  token_count: number;
  tokens_per_word: number;
  tokens_per_character: number;
}

export interface TokenizeResponse {
  tokenizer_mode: TokenizerMode;
  encoding: string | null;
  tokens: Token[];
  stats: Statistics;
}

export type VocabularyEntryStatus = "new" | "existing";

export interface CustomVocabularyEntry {
  id: number;
  token: string;
  frequency: number;
  status: VocabularyEntryStatus;
}

export interface VocabularyResponse {
  entries: CustomVocabularyEntry[];
  total_entries: number;
}

export interface EncodingsResponse {
  encodings: string[];
}

export type ErrorCode =
  | "EMPTY_INPUT"
  | "UNSUPPORTED_FILE_TYPE"
  | "FILE_TOO_LARGE"
  | "INVALID_PDF"
  | "PDF_NO_TEXT"
  | "UNSUPPORTED_ENCODING"
  | "BPE_TRAINING_TEXT_EMPTY"
  | "BPE_TRAINING_TEXT_TOO_LONG"
  | "BPE_TARGET_VOCAB_SIZE_INVALID"
  | "BPE_MODEL_NOT_TRAINED"
  | "BPE_UNKNOWN_CHARACTER";

export interface ErrorResponse {
  error_code: ErrorCode;
  message: string;
}

// --- BPE amendment ---------------------------------------------------------

export interface BpeVocabularyEntry {
  id: number;
  token: string;
}

export interface BpeMergeRule {
  order: number;
  left: string;
  right: string;
  merged: string;
  merged_id: number;
}

export interface BpeTrainingStep {
  step: number;
  pair_selected: [string, string];
  merged_into: string;
}

export interface BpeModelResponse {
  trained: boolean;
  vocabulary: BpeVocabularyEntry[];
  merge_rules: BpeMergeRule[];
  training_steps: BpeTrainingStep[];
  target_vocab_size: number | null;
  achieved_vocab_size: number | null;
}

export interface BpeTrainRequest {
  training_text: string;
  target_vocab_size: number;
}
