export const fmt = (s: string) => new Date(s).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
export const money = (n: number) => (n ? new Intl.NumberFormat(undefined, { style: "currency", currency: import.meta.env.VITE_CURRENCY ?? "INR" }).format(n) : "Free");
export const today = () => new Date().toLocaleDateString("en-CA");
export const STATUSES = ["pending", "waitlisted", "approved", "rejected", "cancelled", "checked_in", "completed", "disputed"];
export const links = (csv: string) => csv.split(",").filter(Boolean);
