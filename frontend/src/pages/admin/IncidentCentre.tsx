import { useState } from "react";
import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import Modal from "../../components/common/Modal";
import StatusBadge from "../../components/common/StatusBadge";
import { useApi } from "../../hooks/useApi";
import { useSubmit } from "../../hooks/useSubmit";
import { api, fileUrl } from "../../services/api";
import { Row } from "../../types";
import { fmt, links } from "../../utils/format";

export default function IncidentCentre() {
  const d = useApi<Row[]>("/incidents?scope=managed");
  const [t, setT] = useState<Row | null>(null);
  const form = useSubmit(async (v) => { await api(`/incidents/${t!.id}`, { method: "PATCH", body: { status: v.status, findings: v.findings || null, resolution: v.resolution || null } }); setT(null); d.reload(); });
  return (
    <>
      <h1>Incident and dispute centre</h1>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="No incidents on record." cols={[
        ["#", (i) => i.id], ["Resource", (i) => i.resource_name], ["Booked by", (i) => i.booked_by], ["Type", (i) => i.kind], ["Raised by", (i) => i.reporter_name],
        ["Details", (i) => <>{i.description} {links(i.evidence_urls).map((u, n) => <a key={u} href={fileUrl(u)} target="_blank" rel="noreferrer">Evidence {n + 1} </a>)}</>],
        ["Opened", (i) => fmt(i.created_at)], ["Status", (i) => <StatusBadge s={i.status} />],
        ["", (i) => ["resolved", "closed"].includes(i.status) ? i.resolution : <button className="btn small" onClick={() => setT(i)}>Investigate</button>],
      ]} />}</Async>
      <Modal open={!!t} title={t ? `Incident #${t.id}` : ""} onClose={() => setT(null)}>
        <form onSubmit={form.onSubmit}>
          <label>Move to<select name="status"><option value="investigating">Investigating</option><option value="resolved">Resolved</option><option value="closed">Closed</option></select></label>
          <label>Findings<textarea name="findings" defaultValue={t?.findings} /></label>
          <label>Resolution<textarea name="resolution" defaultValue={t?.resolution} /></label>
          {form.error && <p role="alert" className="err">{form.error}</p>}
          <button className="btn" disabled={form.busy}>Save</button>{" "}
          <button type="button" className="btn ghost" onClick={() => setT(null)}>Cancel</button>
        </form>
      </Modal>
    </>
  );
}
