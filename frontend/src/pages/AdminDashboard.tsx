import { useState } from "react";
import Async from "../components/common/Async";
import DataTable from "../components/common/DataTable";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { Row } from "../types";

export default function AdminDashboard() {
  const d = useApi<Row>("/admin/stats");
  const [msg, setMsg] = useState("");
  const scan = async () => { const r = await api("/admin/overdue-scan", { body: {} }); setMsg(`${r.alerts} overdue alert(s) sent.`); d.reload(); };
  return (
    <>
      <h1>Admin dashboard</h1>
      <Async d={d}>{(s) => {
        const items: [string, number][] = [["Pending requests", s.pending_requests], ["Upcoming bookings", s.upcoming_bookings], ["Unresolved incidents", s.unresolved_incidents], ["Overdue returns", s.overdue_returns]];
        return (
          <>
            <div className="stats">{items.map(([k, v]) => <div className="stat" key={k}><b>{v}</b><span>{k}</span></div>)}</div>
            <button className="btn ghost" onClick={scan}>Send overdue alerts</button> <span role="status">{msg}</span>
            <h2>Utilisation, last 30 days</h2>
            <DataTable rows={s.utilisation} cols={[["Resource", (r) => r.resource], ["Hours booked", (r) => r.hours_booked], ["Utilisation", (r) => `${r.utilisation_pct}%`]]} />
          </>
        );
      }}</Async>
    </>
  );
}
