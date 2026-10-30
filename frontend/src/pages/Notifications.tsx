import Async from "../components/common/Async";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { Row } from "../types";
import { fmt } from "../utils/format";

export default function Notifications() {
  const d = useApi<Row[]>("/notifications");
  const mark = async (id?: number) => { await api(id ? `/notifications/${id}/read` : "/notifications/read-all", { body: {} }); d.reload(); };
  return (
    <>
      <h1>Notifications</h1>
      <button className="btn ghost" onClick={() => mark()}>Mark all as read</button>
      <Async d={d}>{(rows) => rows.length === 0 ? <p className="muted">No notifications yet.</p> : (
        <ul className="list">{rows.map((n) => (
          <li key={n.id} className={n.read_at ? "" : "unread"}>
            <strong>{n.kind}</strong> {n.message} <time className="muted" dateTime={n.created_at}>{fmt(n.created_at)}</time>
            {!n.read_at && <button className="btn ghost small" onClick={() => mark(n.id)}>Mark read</button>}
          </li>
        ))}</ul>
      )}</Async>
    </>
  );
}
