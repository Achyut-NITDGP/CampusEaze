import { useSearchParams } from "react-router-dom";
import Async from "../components/common/Async";
import DataTable from "../components/common/DataTable";
import StatusBadge from "../components/common/StatusBadge";
import { useAuth } from "../contexts/AuthContext";
import { useApi } from "../hooks/useApi";
import { useSubmit } from "../hooks/useSubmit";
import { api, upload } from "../services/api";
import { Booking, Row } from "../types";
import { fmt } from "../utils/format";

export default function Incidents() {
  const [q] = useSearchParams();
  const { user } = useAuth();
  const d = useApi<Row[]>("/incidents");
  const bs = useApi<Booking[]>(`/bookings?scope=${user?.role === "user" ? "mine" : "managed"}`);
  const { onSubmit, error, busy } = useSubmit(async (v, f) => {
    const file = (f.elements.namedItem("evidence") as HTMLInputElement).files?.[0];
    await api("/incidents", { body: { booking_id: Number(v.booking_id), kind: v.kind, description: v.description, evidence_urls: file ? [await upload(file)] : [] } });
    f.reset(); d.reload();
  });
  const eligible = (bs.data ?? []).filter((b) => ["approved", "checked_in", "completed", "disputed"].includes(b.status));
  return (
    <>
      <h1>Disputes and incidents</h1>
      <h2>Report a problem</h2>
      <form onSubmit={onSubmit}>
        <label>Booking
          <select name="booking_id" required defaultValue={q.get("booking") ?? ""}>
            <option value="" disabled>Choose a booking</option>
            {eligible.map((b) => <option key={b.id} value={b.id}>#{b.id} {b.resource_name}, {fmt(b.start_time)}</option>)}
          </select>
        </label>
        <label>Type<select name="kind"><option value="damage">Damage</option><option value="delay">Delay</option><option value="dispute">Disagreement</option></select></label>
        <label>What happened<textarea name="description" required minLength={5} /></label>
        <label>Evidence (optional)<input type="file" name="evidence" accept="image/*,application/pdf" /></label>
        {error && <p role="alert" className="err">{error}</p>}
        <button className="btn" disabled={busy}>Send report</button>
      </form>
      <h2>Your incidents</h2>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="No incidents. Good." cols={[
        ["#", (i) => i.id], ["Resource", (i) => i.resource_name], ["Type", (i) => i.kind], ["Status", (i) => <StatusBadge s={i.status} />],
        ["Findings", (i) => i.findings || "Waiting for review"], ["Resolution", (i) => i.resolution || "-"],
      ]} />}</Async>
    </>
  );
}
