import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="nav">
      <Link to="/" className="brand"><img src="/logo.svg" alt="" width="28" height="28" /> Unlock</Link>
      <nav aria-label="Main">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/resources">Search</NavLink>
        <NavLink to="/bookings">My bookings</NavLink>
        <NavLink to="/incidents">Incidents</NavLink>
        <NavLink to="/notifications">Notifications</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        {user && user.role !== "user" && <NavLink to="/admin">Admin</NavLink>}
      </nav>
      <button className="btn ghost" onClick={logout}>Sign out</button>
    </header>
  );
}
