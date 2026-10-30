import { useNavigate, useParams } from "react-router-dom";
import Async from "../components/common/Async";
import { useApi } from "../hooks/useApi";
import { useSubmit } from "../hooks/useSubmit";
import { api, upload } from "../services/api";
import { links } from "../utils/format";

export default function CheckInOut() {
  const { id } = useParams();
  const nav = useNavigate();
  const d = useApi<any>(`/bookings/${id}`);
  const mode = d.data?.status === "approved" ? "check-in" : "check-out";
  const { onSubmit, error, busy } = useSubmit(async (v, f) => {
    const files = Array.from((f.elements.namedItem("photos") as HTMLInputElement).files ?? []);
    const photo_urls = await Promise.all(files.map((x) => upload(x)));
    await api(`/handover/${id}/${mode}`, { body: { condition_notes: v.notes, checklist_ok: v.checklist_ok === "on", damage_reported: v.damage_reported === "on", photo_urls } });
    nav(`/bookings/${id}`);
  });
  return (
    <Async d={d}>{(b) => !["approved", "checked_in"].includes(b.status) ? <p>This booking cannot be checked in or out right now.</p> : (
      <>
        <h1>{mode === "check-in" ? "Check in" : "Check out"}: {b.resource_name}</h1>
        {mode === "check-out" && b.reports.map((r: any) => <p key={r.id} className="muted">Condition at check-in: {r.condition_notes || "no notes"} {links(r.photo_urls).length} photo(s).</p>)}
        <form onSubmit={onSubmit}>
          <label>Condition notes<textarea name="notes" required /></label>
          <label className="inline"><input type="checkbox" name="checklist_ok" defaultChecked /> Everything is present and working</label>
          {mode === "check-out" && <label className="inline"><input type="checkbox" name="damage_reported" /> I noticed damage (sends this to human review)</label>}
          <label>Photos<input type="file" name="photos" accept="image/*" multiple /></label>
          {error && <p role="alert" className="err">{error}</p>}
          <button className="btn" disabled={busy}>{mode === "check-in" ? "Confirm handover" : "Confirm return"}</button>
        </form>
      </>
    )}</Async>
  );
}
