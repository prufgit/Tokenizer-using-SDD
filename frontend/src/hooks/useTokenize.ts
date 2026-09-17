import { useCallback, useState } from "react";

import { ApiError, tokenize, type TokenizeParams } from "../api/tokenizerClient";
import type { RequestState } from "../components/results/StateBanner";
import type { TokenizeResponse } from "../types/api";

export function useTokenize(onCustomTokenizeSuccess?: () => void) {
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [result, setResult] = useState<TokenizeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const run = useCallback(
    async (params: TokenizeParams) => {
      setRequestState("loading");
      setErrorMessage(null);
      try {
        const response = await tokenize(params);
        setResult(response);
        setRequestState("success");
        if (params.tokenizerMode === "custom") {
          onCustomTokenizeSuccess?.();
        }
      } catch (error) {
        const message =
          error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
        setErrorMessage(message);
        setRequestState("error");
      }
    },
    [onCustomTokenizeSuccess]
  );

  return { requestState, result, errorMessage, run };
}
