import { useState } from "react";
import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import StatusBadge from "../../components/common/StatusBadge";
import { useAuth } from "../../contexts/AuthContext";
import { useApi } from "../../hooks/useApi";
import { api, fileUrl } from "../../services/api";
import { Row } from "../../types";
import { fmt } from "../../utils/format";

export default function UsersVerification() {
  const { user: me } = useAuth();
  const users = useApi<Row[]>("/users");
  const pending = useApi<Row[]>("/eligibility?status=pending");
  const [err, setErr] = useState("");
  const run = async (fn: () => Promise<unknown>) => { try { setErr(""); await fn(); users.reload(); pending.reload(); } catch (e: any) { setErr(e.message); } };
  const patch = (id: number, body: Row) => run(() => api(`/users/${id}`, { method: "PATCH", body }));
  const review = (id: number, status: string) => run(() => api(`/eligibility/${id}`, { method: "PATCH", body: { status } }));
  return (
    <>
      <h1>Users and verification</h1>
      {err && <p role="alert" className="err">{err}</p>}
      <h2>Waiting for verification</h2>
      <Async d={pending}>{(rows) => <DataTable rows={rows} empty="Nothing waiting." cols={[
        ["User", (r) => r.user_name], ["Submitted", (r) => r.requirement_type], ["When", (r) => fmt(r.created_at)],
        ["Document", (r) => r.document_url ? <a href={fileUrl(r.document_url)} target="_blank" rel="noreferrer">View</a> : "None"],
        ["Decision", (r) => <span className="actions"><button className="btn small" onClick={() => review(r.id, "verified")}>Verify</button><button className="btn ghost small" onClick={() => review(r.id, "rejected")}>Reject</button></span>],
      ]} />}</Async>
      <h2>All accounts</h2>
      <Async d={users}>{(rows) => <DataTable rows={rows} cols={[
        ["Name", (u) => u.name], ["Email", (u) => u.email],
        ["Role", (u) => me?.role === "admin" && u.id !== me.id
          ? <select aria-label={`Role for ${u.name}`} value={u.role} onChange={(e) => patch(u.id, { role: e.target.value })}>{["user", "owner", "manager", "admin"].map((r) => <option key={r}>{r}</option>)}</select> : u.role],
        ["Identity", (u) => <StatusBadge s={u.verification_status} />],
        ["Access", (u) => u.id === me?.id ? "You" : <button className="btn ghost small" onClick={() => patch(u.id, { active: !u.active })}>{u.active ? "Suspend" : "Restore"}</button>],
      ]} />}</Async>
    </>
  );
}
