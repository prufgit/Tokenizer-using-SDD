import type {
  BpeModelResponse,
  BpeTrainRequest,
  EncodingsResponse,
  ErrorResponse,
  TokenizeResponse,
  TokenizerMode,
  VocabularyResponse,
} from "../types/api";

const API_BASE_URL: string =
  (import.meta as unknown as { env: Record<string, string | undefined> }).env
    ?.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  errorCode: ErrorResponse["error_code"] | "UNKNOWN";

  constructor(body: Partial<ErrorResponse> | undefined, fallbackMessage: string) {
    super(body?.message ?? fallbackMessage);
    this.errorCode = body?.error_code ?? "UNKNOWN";
  }
}

async function parseErrorOrThrow(response: Response): Promise<never> {
  let body: Partial<ErrorResponse> | undefined;
  try {
    body = (await response.json()) as Partial<ErrorResponse>;
  } catch {
    body = undefined;
  }
  throw new ApiError(body, `Request failed with status ${response.status}`);
}

export interface TokenizeParams {
  text?: string;
  file?: File;
  tokenizerMode: TokenizerMode;
  encoding?: string;
}

export async function tokenize(params: TokenizeParams): Promise<TokenizeResponse> {
  const form = new FormData();
  if (params.file) {
    form.append("file", params.file);
  } else if (params.text !== undefined) {
    form.append("text", params.text);
  }
  form.append("tokenizer_mode", params.tokenizerMode);
  if (params.encoding) {
    form.append("encoding", params.encoding);
  }

  const response = await fetch(`${API_BASE_URL}/api/tokenize`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    await parseErrorOrThrow(response);
  }
  return (await response.json()) as TokenizeResponse;
}

export async function getEncodings(): Promise<EncodingsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/encodings`);
  if (!response.ok) {
    await parseErrorOrThrow(response);
  }
  return (await response.json()) as EncodingsResponse;
}

export async function getVocabulary(): Promise<VocabularyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/vocabulary`);
  if (!response.ok) {
    await parseErrorOrThrow(response);
  }
  return (await response.json()) as VocabularyResponse;
}

export async function resetVocabulary(): Promise<VocabularyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/vocabulary/reset`, {
    method: "POST",
  });
  if (!response.ok) {
    await parseErrorOrThrow(response);
  }
  return (await response.json()) as VocabularyResponse;
}

export async function trainBpe(request: BpeTrainRequest): Promise<BpeModelResponse> {
  const response = await fetch(`${API_BASE_URL}/api/bpe/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    await parseErrorOrThrow(response);
  }
  return (await response.json()) as BpeModelResponse;
}

export async function getBpeModel(): Promise<BpeModelResponse> {
  const response = await fetch(`${API_BASE_URL}/api/bpe/model`);
  if (!response.ok) {
    await parseErrorOrThrow(response);
  }
  return (await response.json()) as BpeModelResponse;
}
