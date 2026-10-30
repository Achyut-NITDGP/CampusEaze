import { useState } from "react";
import Async from "../../components/common/Async";
import { useApi } from "../../hooks/useApi";
import { useSubmit } from "../../hooks/useSubmit";
import { api } from "../../services/api";
import { Row } from "../../types";

export default function AdminNotifications() {
  const users = useApi<Row[]>("/users");
  const [msg, setMsg] = useState("");
  const send = useSubmit(async (v, f) => { const r = await api("/notifications/send", { body: { user_id: v.user_id ? Number(v.user_id) : null, message: v.message } }); setMsg(`Sent to ${r.sent} user(s).`); f.reset(); });
  const scan = async () => { const r = await api("/admin/overdue-scan", { body: {} }); setMsg(`${r.alerts} overdue alert(s) sent.`); };
  return (
    <>
      <h1>Notifications</h1>
      <Async d={users}>{(rows) => (
        <form onSubmit={send.onSubmit}>
          <label>Send to<select name="user_id"><option value="">Everyone</option>{rows.map((u) => <option key={u.id} value={u.id}>{u.name} ({u.email})</option>)}</select></label>
          <label>Message<textarea name="message" required minLength={3} maxLength={500} /></label>
          {send.error && <p role="alert" className="err">{send.error}</p>}
          <button className="btn" disabled={send.busy}>Send notification</button>
        </form>
      )}</Async>
      <h2>Overdue returns</h2>
      <p>Alert people who are still holding a resource past the end of their booking.</p>
      <button className="btn ghost" onClick={scan}>Send overdue alerts</button>
      <p role="status">{msg}</p>
    </>
  );
}
