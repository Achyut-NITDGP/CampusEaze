const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, public detail: any) {
    super(typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((d: any) => d.msg).join("; ") : detail?.message ?? "Something went wrong. Try again.");
  }
}

export const fileUrl = (u: string) => (u.startsWith("http") ? u : BASE + u);

async function call<T>(path: string, init: RequestInit): Promise<T> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const r = await fetch(`${BASE}/api/v1${path}`, { ...init, headers });
  const data = await r.json().catch(() => null);
  if (!r.ok) {
    if (r.status === 401 && token && !path.startsWith("/auth")) { localStorage.removeItem("token"); location.href = "/login"; }
    throw new ApiError(r.status, data?.detail);
  }
  return data as T;
}

export const api = <T = any>(path: string, opts: { method?: string; body?: unknown } = {}) =>
  call<T>(path, {
    method: opts.method ?? (opts.body !== undefined ? "POST" : "GET"),
    headers: { "Content-Type": "application/json" },
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });

export async function upload(file: File): Promise<string> {
  const fd = new FormData();
  fd.append("file", file);
  return (await call<{ url: string }>("/handover/upload", { method: "POST", body: fd })).url;
}
