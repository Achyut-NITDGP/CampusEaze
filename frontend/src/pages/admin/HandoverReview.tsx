import { useState } from "react";
import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import Modal from "../../components/common/Modal";
import { useApi } from "../../hooks/useApi";
import { useSubmit } from "../../hooks/useSubmit";
import { api, fileUrl } from "../../services/api";
import { Row } from "../../types";
import { fmt, links } from "../../utils/format";

export default function HandoverReview() {
  const [flagged, setFlagged] = useState(true);
  const d = useApi<Row[]>(`/handover/reports?flagged=${flagged}`);
  const [t, setT] = useState<Row | null>(null);
  const form = useSubmit(async (v) => { await api(`/handover/reports/${t!.id}/review`, { body: { outcome: v.outcome, note: v.note } }); setT(null); d.reload(); });
  return (
    <>
      <h1>Handover and return review</h1>
      <label className="inline"><input type="checkbox" checked={flagged} onChange={(e) => setFlagged(e.target.checked)} /> Only flagged reports that still need a decision</label>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="No reports need review." cols={[
        ["Resource", (r) => r.resource_name], ["User", (r) => r.user_name], ["Type", (r) => r.report_type], ["When", (r) => fmt(r.created_at)],
        ["Notes", (r) => r.condition_notes || "-"], ["Checklist", (r) => r.checklist_ok ? "Passed" : "Not passed"],
        ["Photos", (r) => links(r.photo_urls).map((u, i) => <a key={u} href={fileUrl(u)} target="_blank" rel="noreferrer">{i + 1} </a>)],
        ["Review", (r) => r.reviewed_by ? `${r.review_outcome?.replace("_", " ")}: ${r.review_note}` : r.flagged ? <button className="btn small" onClick={() => setT(r)}>Review</button> : "No flag"],
      ]} />}</Async>
      <Modal open={!!t} title="Review flagged report" onClose={() => setT(null)}>
        <form onSubmit={form.onSubmit}>
          <label>Outcome<select name="outcome"><option value="discrepancy_confirmed">Confirm the discrepancy</option><option value="cleared">Clear the flag</option></select></label>
          <label>Note<textarea name="note" required minLength={3} /></label>
          {form.error && <p role="alert" className="err">{form.error}</p>}
          <button className="btn" disabled={form.busy}>Save review</button>{" "}
          <button type="button" className="btn ghost" onClick={() => setT(null)}>Cancel</button>
        </form>
      </Modal>
    </>
  );
}
