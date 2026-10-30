import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSubmit } from "../../hooks/useSubmit";
import * as bookingService from "../../services/bookingService";
import { Row } from "../../types";
import { money } from "../../utils/format";

export default function BookingForm({ resource, start, end }: { resource: Row; start: string; end: string }) {
  const nav = useNavigate();
  const [issues, setIssues] = useState<string[]>([]);
  const hours = (new Date(end).getTime() - new Date(start).getTime()) / 36e5;
  const total = hours * resource.price_per_hour;
  const { onSubmit, error, busy } = useSubmit(async (v) => {
    setIssues([]);
    try {
      const b = await bookingService.create({ resource_id: resource.id, start_time: start, end_time: end, purpose: v.purpose });
      nav(`/bookings/${b.id}`);
    } catch (e: any) {
      if (e.detail?.issues) setIssues(e.detail.issues);
      throw e;
    }
  });
  return (
    <form onSubmit={onSubmit}>
      <label>Purpose of use<textarea name="purpose" required minLength={3} maxLength={500} /></label>
      <p>Duration: {hours} h. Total: {money(total)}{total > 0 && " (payment is simulated in this prototype)"}</p>
      {issues.length > 0 && <ul className="err">{issues.map((i) => <li key={i}>{i}</li>)}</ul>}
      {error && <p role="alert" className="err">{error}</p>}
      <button className="btn" disabled={busy}>Send request</button>
    </form>
  );
}
