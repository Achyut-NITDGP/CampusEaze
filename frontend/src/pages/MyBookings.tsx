import { useState } from "react";
import { Link } from "react-router-dom";
import Async from "../components/common/Async";
import DataTable from "../components/common/DataTable";
import StatusBadge from "../components/common/StatusBadge";
import { useApi } from "../hooks/useApi";
import { Booking } from "../types";
import { fmt, money, STATUSES } from "../utils/format";

export default function MyBookings() {
  const [s, setS] = useState("");
  const d = useApi<Booking[]>(`/bookings?scope=mine${s ? `&status=${s}` : ""}`);
  return (
    <>
      <h1>My bookings</h1>
      <label>Show<select value={s} onChange={(e) => setS(e.target.value)}><option value="">All statuses</option>{STATUSES.map((x) => <option key={x} value={x}>{x.replace("_", " ")}</option>)}</select></label>
      <Async d={d}>{(rows) => (
        <DataTable rows={rows} empty="No bookings yet. Search for a resource to make your first request." cols={[
          ["Resource", (b) => b.resource_name], ["When", (b) => fmt(b.start_time)], ["Cost", (b) => money(b.amount)],
          ["Status", (b) => <><StatusBadge s={b.status} />{b.waitlist_position ? ` #${b.waitlist_position} in line` : ""}</>],
          ["", (b) => <Link to={`/bookings/${b.id}`}>Open</Link>],
        ]} />
      )}</Async>
    </>
  );
}
