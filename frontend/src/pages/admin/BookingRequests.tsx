import { useState } from "react";
import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import Modal from "../../components/common/Modal";
import StatusBadge from "../../components/common/StatusBadge";
import { useApi } from "../../hooks/useApi";
import { useSubmit } from "../../hooks/useSubmit";
import * as bookingService from "../../services/bookingService";
import { Booking } from "../../types";
import { fmt, money } from "../../utils/format";

export default function BookingRequests() {
  const [f, setF] = useState("pending");
  const d = useApi<Booking[]>(`/bookings?scope=managed&status=${f}`);
  const [t, setT] = useState<{ b: Booking; decision: string } | null>(null);
  const [err, setErr] = useState("");
  const form = useSubmit(async (v) => { await bookingService.decide(t!.b.id, t!.decision, v.reason); setT(null); d.reload(); });
  const approve = async (b: Booking) => { try { setErr(""); await bookingService.decide(b.id, "approve", ""); d.reload(); } catch (e: any) { setErr(e.message); } };
  return (
    <>
      <h1>Booking requests</h1>
      <label>Show<select value={f} onChange={(e) => setF(e.target.value)}><option value="pending">Pending</option><option value="waitlisted">Waiting list</option></select></label>
      {err && <p role="alert" className="err">{err}</p>}
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="No requests to review." cols={[
        ["Resource", (b) => b.resource_name], ["Requested by", (b) => b.user_name], ["When", (b) => fmt(b.start_time)], ["Purpose", (b) => b.purpose], ["Paid", (b) => money(b.amount)],
        ["System check", (b) => b.has_conflict ? "Overlaps an approved booking or block" : "No conflict found"],
        ["Decision", (b) => <span className="actions">
          <StatusBadge s={b.status} />
          <button className="btn small" onClick={() => approve(b)}>Approve</button>
          <button className="btn ghost small" onClick={() => setT({ b, decision: "waitlist" })}>Waitlist</button>
          <button className="btn ghost small" onClick={() => setT({ b, decision: "reject" })}>Reject</button>
        </span>],
      ]} />}</Async>
      <Modal open={!!t} title={t ? `${t.decision === "reject" ? "Reject" : "Waitlist"} request #${t.b.id}` : ""} onClose={() => setT(null)}>
        <form onSubmit={form.onSubmit}>
          <label>Reason (the requester will see this)<textarea name="reason" required minLength={3} /></label>
          {form.error && <p role="alert" className="err">{form.error}</p>}
          <button className="btn" disabled={form.busy}>Record decision</button>{" "}
          <button type="button" className="btn ghost" onClick={() => setT(null)}>Cancel</button>
        </form>
      </Modal>
    </>
  );
}
