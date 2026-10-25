import { useEffect, useState } from "react";

interface Stored<T> {
  key: string;
  data: T | null;
  error: string | null;
}

export function useFetched<T>(key: string, enabled: boolean, load: () => Promise<T>) {
  const [state, setState] = useState<Stored<T> | null>(null);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    load()
      .then((data) => !cancelled && setState({ key, data, error: null }))
      .catch((e: Error) => !cancelled && setState({ key, data: null, error: e.message }));
    return () => {
      cancelled = true;
    };
  }, [key, enabled]);

  const current = state?.key === key ? state : null;
  return {
    data: current?.data ?? null,
    error: current?.error ?? null,
    loading: enabled && current === null,
  };
}