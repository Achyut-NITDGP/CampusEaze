import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useSubmit } from "../hooks/useSubmit";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const { onSubmit, error, busy } = useSubmit(async (v) => { await register(v); nav("/"); });
  return (
    <main className="auth">
      <h1>Create your account</h1>
      <form onSubmit={onSubmit}>
        <label>Full name<input name="name" autoComplete="name" required minLength={2} /></label>
        <label>Email<input name="email" type="email" autoComplete="email" required /></label>
        <label>Password (8 characters or more)<input name="password" type="password" autoComplete="new-password" required minLength={8} /></label>
        <label>I want to
          <select name="role"><option value="user">Borrow equipment and spaces</option><option value="owner">Share my own equipment and spaces</option></select>
        </label>
        {error && <p role="alert" className="err">{error}</p>}
        <button className="btn" disabled={busy}>Create account</button>
      </form>
      <p>Already registered? <Link to="/login">Sign in</Link></p>
    </main>
  );
}
