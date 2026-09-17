import { useCallback, useState } from "react";

import { getBpeModel } from "../api/tokenizerClient";
import type { BpeModelResponse } from "../types/api";

export function useBpeModel() {
  const [model, setModel] = useState<BpeModelResponse | null>(null);

  const refresh = useCallback(async () => {
    const response = await getBpeModel();
    setModel(response);
  }, []);

  return { model, refresh };
}
