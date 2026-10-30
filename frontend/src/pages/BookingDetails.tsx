import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import Async from "../components/common/Async";
import BookingTimeline from "../components/bookings/BookingTimeline";
import StatusBadge from "../components/common/StatusBadge";
import { useAuth } from "../contexts/AuthContext";
import { useApi } from "../hooks/useApi";
import { fileUrl } from "../services/api";
import * as bookingService from "../services/bookingService";
import { fmt, links, money } from "../utils/format";

export default function BookingDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const d = useApi<any>(`/bookings/${id}`);
  const [err, setErr] = useState("");
  return (
    <Async d={d}>{(b) => {
      const mine = b.user_id === user?.id;
      const cancel = async () => { try { await bookingService.cancel(b.id); d.reload(); } catch (e: any) { setErr(e.message); } };
      return (
        <>
          <h1>{b.resource_name}</h1>
          <p><StatusBadge s={b.status} /> {b.waitlist_position ? `Waiting list position ${b.waitlist_position}` : ""}</p>
          <dl className="facts">
            <dt>Booked by</dt><dd>{b.user_name}</dd>
            <dt>When</dt><dd>{fmt(b.start_time)} to {fmt(b.end_time)}</dd>
            <dt>Purpose</dt><dd>{b.purpose}</dd>
            <dt>Cost</dt><dd>{money(b.amount)} ({b.payment_status.replace("_", " ")})</dd>
          </dl>
          {err && <p role="alert" className="err">{err}</p>}
          <div className="actions">
            {mine && (b.status === "approved" || b.status === "checked_in") && <Link className="btn" to={`/bookings/${b.id}/handover`}>{b.status === "approved" ? "Check in" : "Check out"}</Link>}
            {["pending", "waitlisted", "approved"].includes(b.status) && <button className="btn ghost" onClick={cancel}>Cancel booking</button>}
            {["approved", "checked_in", "completed", "disputed"].includes(b.status) && <Link className="btn ghost" to={`/incidents?booking=${b.id}`}>Report an issue</Link>}
          </div>
          <h2>Timeline</h2>
          <BookingTimeline events={b.timeline} />
          {b.reports.length > 0 && <>
            <h2>Condition reports</h2>
            {b.reports.map((r: any) => (
              <article className="card" key={r.id}>
                <h3>{r.report_type === "checkin" ? "At check-in" : "At return"} {r.flagged && <span className="badge disputed">flagged</span>}</h3>
                <p>{r.condition_notes || "No notes."} Checklist {r.checklist_ok ? "passed" : "not passed"}.</p>
                {links(r.photo_urls).map((u, i) => <a key={u} href={fileUrl(u)} target="_blank" rel="noreferrer">Photo {i + 1} </a>)}
              </article>
            ))}
          </>}
        </>
      );
    }}</Async>
  );
}
