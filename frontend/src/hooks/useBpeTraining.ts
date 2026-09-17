import { useCallback, useState } from "react";

import { ApiError, trainBpe } from "../api/tokenizerClient";
import type { RequestState } from "../components/results/StateBanner";
import type { BpeModelResponse, BpeTrainRequest } from "../types/api";

export function useBpeTraining(onTrainingSuccess?: () => void) {
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [result, setResult] = useState<BpeModelResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const train = useCallback(
    async (request: BpeTrainRequest) => {
      setRequestState("loading");
      setErrorMessage(null);
      try {
        const response = await trainBpe(request);
        setResult(response);
        setRequestState("success");
        onTrainingSuccess?.();
      } catch (error) {
        const message =
          error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
        setErrorMessage(message);
        setRequestState("error");
      }
    },
    [onTrainingSuccess]
  );

  return { requestState, result, errorMessage, train };
}
