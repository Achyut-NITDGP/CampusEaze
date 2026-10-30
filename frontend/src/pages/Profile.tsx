import Async from "../components/common/Async";
import DataTable from "../components/common/DataTable";
import StatusBadge from "../components/common/StatusBadge";
import { useAuth } from "../contexts/AuthContext";
import { useApi } from "../hooks/useApi";
import { useSubmit } from "../hooks/useSubmit";
import { api, fileUrl, upload } from "../services/api";
import { Row } from "../types";
import { fmt } from "../utils/format";

export default function Profile() {
  const { user } = useAuth();
  const d = useApi<Row[]>("/eligibility/me");
  const name = useSubmit(async (v) => { await api("/users/me", { method: "PATCH", body: { name: v.name } }); location.reload(); });
  const doc = useSubmit(async (v, f) => {
    const file = (f.elements.namedItem("doc") as HTMLInputElement).files?.[0];
    await api("/eligibility", { body: { requirement_type: v.requirement_type, document_url: file ? await upload(file) : null } });
    f.reset(); d.reload();
  });
  return (
    <>
      <h1>Profile</h1>
      <form onSubmit={name.onSubmit}>
        <label>Name<input name="name" defaultValue={user?.name} required minLength={2} /></label>
        <p>Email: {user?.email}. Role: {user?.role}. Identity: <StatusBadge s={user?.verification_status ?? "unverified"} /></p>
        {name.error && <p role="alert" className="err">{name.error}</p>}
        <button className="btn ghost" disabled={name.busy}>Save name</button>
      </form>
      <h2>Verification documents and qualifications</h2>
      <form onSubmit={doc.onSubmit}>
        <label>What are you submitting?<input name="requirement_type" required placeholder="identity, or the exact qualification name, e.g. 3D Printer Training" /></label>
        <label>Document (PDF or image)<input type="file" name="doc" accept="image/*,application/pdf" required /></label>
        {doc.error && <p role="alert" className="err">{doc.error}</p>}
        <button className="btn" disabled={doc.busy}>Submit for verification</button>
      </form>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="Nothing submitted yet." cols={[
        ["Type", (r) => r.requirement_type], ["Submitted", (r) => fmt(r.created_at)], ["Status", (r) => <StatusBadge s={r.status} />],
        ["Document", (r) => r.document_url ? <a href={fileUrl(r.document_url)} target="_blank" rel="noreferrer">View</a> : "-"],
      ]} />}</Async>
    </>
  );
}
