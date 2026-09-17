import { useCallback, useState } from "react";

import { getVocabulary, resetVocabulary } from "../api/tokenizerClient";
import type { VocabularyResponse } from "../types/api";

export function useVocabulary() {
  const [vocabulary, setVocabulary] = useState<VocabularyResponse | null>(null);

  const refresh = useCallback(async () => {
    const response = await getVocabulary();
    setVocabulary(response);
  }, []);

  const reset = useCallback(async () => {
    const response = await resetVocabulary();
    setVocabulary(response);
  }, []);

  return { vocabulary, refresh, reset };
}
