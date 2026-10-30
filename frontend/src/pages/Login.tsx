import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useSubmit } from "../hooks/useSubmit";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const { onSubmit, error, busy } = useSubmit(async (v) => { await login(v.email, v.password); nav("/"); });
  return (
    <main className="auth">
      <h1>Sign in to Unlock</h1>
      <form onSubmit={onSubmit}>
        <label>Email<input name="email" type="email" autoComplete="email" required /></label>
        <label>Password<input name="password" type="password" autoComplete="current-password" required /></label>
        {error && <p role="alert" className="err">{error}</p>}
        <button className="btn" disabled={busy}>Sign in</button>
      </form>
      <p>New here? <Link to="/register">Create an account</Link></p>
      <p className="muted">Demo: admin@demo.edu, owner@demo.edu or student@demo.edu with password Demo@12345</p>
    </main>
  );
}
