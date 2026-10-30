import { useNavigate, useParams } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import { useSubmit } from "../hooks/useSubmit";
import * as resourceService from "../services/resourceService";
import { Row } from "../types";
import { fmt } from "../utils/format";

export default function CreateResource() {
  const { id } = useParams();
  const nav = useNavigate();
  const d = useApi<Row>(id ? `/resources/${id}` : null);
  const r: Row = d.data ?? {};
  const form = useSubmit(async (v) => {
    await resourceService.save(id, {
      name: v.name, description: v.description, category: v.category, location: v.location, price_per_hour: Number(v.price_per_hour || 0), rules: v.rules,
      required_qualification: v.required_qualification || null, requires_verification: v.requires_verification === "on", photo_url: v.photo_url || null, status: v.status,
    });
    nav("/admin/resources");
  });
  const blk = useSubmit(async (v, f) => { await resourceService.block(id!, { start_time: v.start, end_time: v.end, reason: v.reason || "Blocked" }); f.reset(); d.reload(); });
  if (id && !d.data) return d.error ? <p role="alert" className="err">{d.error}</p> : <p aria-busy="true">Loading…</p>;
  return (
    <>
      <h1>{id ? "Edit resource" : "Add a resource"}</h1>
      <form onSubmit={form.onSubmit}>
        <label>Name<input name="name" required defaultValue={r.name} /></label>
        <label>Description<textarea name="description" defaultValue={r.description} /></label>
        <label>Category<select name="category" defaultValue={r.category ?? "equipment"}><option value="equipment">Equipment</option><option value="space">Space</option><option value="service">Service</option></select></label>
        <label>Location<input name="location" required defaultValue={r.location} /></label>
        <label>Price per hour (0 for free)<input name="price_per_hour" type="number" min="0" step="0.01" defaultValue={r.price_per_hour ?? 0} /></label>
        <label>Rules for users<textarea name="rules" defaultValue={r.rules} /></label>
        <label>Required qualification (optional)<input name="required_qualification" defaultValue={r.required_qualification ?? ""} /></label>
        <label className="inline"><input type="checkbox" name="requires_verification" defaultChecked={r.requires_verification ?? true} /> Users must have a verified identity</label>
        <label>Photo URL (optional)<input name="photo_url" defaultValue={r.photo_url ?? ""} /></label>
        <label>Status<select name="status" defaultValue={r.status ?? "active"}><option value="active">Active</option><option value="maintenance">Maintenance</option><option value="inactive">Inactive</option></select></label>
        {form.error && <p role="alert" className="err">{form.error}</p>}
        <button className="btn" disabled={form.busy}>Save resource</button>
      </form>
      {id && (
        <>
          <h2>Block unavailable slots</h2>
          <ul className="list">{(r.blocks ?? []).map((b: Row) => <li key={b.id}>{fmt(b.start_time)} to {fmt(b.end_time)}: {b.reason}</li>)}</ul>
          <form onSubmit={blk.onSubmit}>
            <label>From<input type="datetime-local" name="start" required /></label>
            <label>Until<input type="datetime-local" name="end" required /></label>
            <label>Reason<input name="reason" placeholder="Maintenance" /></label>
            {blk.error && <p role="alert" className="err">{blk.error}</p>}
            <button className="btn ghost" disabled={blk.busy}>Block this time</button>
          </form>
        </>
      )}
    </>
  );
}
