import { User } from "../types";
import { api } from "./api";

export const login = (email: string, password: string) => api<{ access_token: string; user: User }>("/auth/login", { body: { email, password } });
export const register = (d: Record<string, string>) => api("/auth/register", { body: d });
export const me = () => api<User>("/auth/me");
