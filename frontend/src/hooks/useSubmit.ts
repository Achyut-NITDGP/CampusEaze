import { FormEvent, useState } from "react";

/** Wraps a form: collects FormData, tracks busy/error state, surfaces the server's message. */
export function useSubmit(fn: (v: Record<string, string>, form: HTMLFormElement) => Promise<unknown>) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    setBusy(true); setError("");
    try { await fn(Object.fromEntries(new FormData(form)) as Record<string, string>, form); }
    catch (x: any) { setError(x.message); }
    finally { setBusy(false); }
  };
  return { onSubmit, error, busy };
}
