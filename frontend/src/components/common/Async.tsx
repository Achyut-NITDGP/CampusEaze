import { ReactNode } from "react";

export default function Async<T>({ d, children }: { d: { data: T | null; error: string; loading: boolean }; children: (data: T) => ReactNode }) {
  if (d.error) return <p role="alert" className="err">{d.error}</p>;
  if (d.loading && !d.data) return <p aria-busy="true">Loading…</p>;
  if (!d.data) return null;
  return <>{children(d.data)}</>;
}
