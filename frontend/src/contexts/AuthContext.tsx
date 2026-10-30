import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import * as auth from "../services/authService";
import { User } from "../types";

interface Ctx { user: User | null; loading: boolean; login: (e: string, p: string) => Promise<void>; register: (d: Record<string, string>) => Promise<void>; logout: () => void }
const C = createContext<Ctx>(null!);
export const useAuth = () => useContext(C);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!localStorage.getItem("token")) { setLoading(false); return; }
    auth.me().then(setUser).catch(() => localStorage.removeItem("token")).finally(() => setLoading(false));
  }, []);
  const login = async (e: string, p: string) => { const r = await auth.login(e, p); localStorage.setItem("token", r.access_token); setUser(r.user); };
  const register = async (d: Record<string, string>) => { await auth.register(d); await login(d.email, d.password); };
  const logout = () => { localStorage.removeItem("token"); setUser(null); };
  return <C.Provider value={{ user, loading, login, register, logout }}>{children}</C.Provider>;
}
