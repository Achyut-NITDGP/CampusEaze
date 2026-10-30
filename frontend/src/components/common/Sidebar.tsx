import { NavLink } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const LINKS: [string, string, boolean][] = [
  ["/admin", "Dashboard", false], ["/admin/requests", "Booking requests", false], ["/admin/handover", "Handover review", false],
  ["/admin/inventory", "Asset inventory", false], ["/admin/resources", "Resource management", false], ["/admin/incidents", "Incident centre", false],
  ["/admin/users", "Users and verification", true], ["/admin/transactions", "Transactions", true], ["/admin/audit", "Audit logs", true], ["/admin/notifications", "Notifications", true],
];

export default function Sidebar() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin" || user?.role === "manager";
  return (
    <nav className="side" aria-label="Admin">
      {LINKS.filter(([, , adminOnly]) => isAdmin || !adminOnly).map(([to, label]) => <NavLink key={to} to={to} end={to === "/admin"}>{label}</NavLink>)}
    </nav>
  );
}
