import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Async from "../components/common/Async";
import AvailabilityCalendar from "../components/resources/AvailabilityCalendar";
import { useApi } from "../hooks/useApi";
import { fileUrl } from "../services/api";
import { Row } from "../types";
import { money, today } from "../utils/format";

export default function ResourceDetails() {
  const { id } = useParams();
  const nav = useNavigate();
  const d = useApi<Row>(`/resources/${id}`);
  const [day, setDay] = useState(today());
  const [sel, setSel] = useState<[string, string] | null>(null);
  return (
    <Async d={d}>{(r) => (
      <>
        <h1>{r.name}</h1>
        <p className="muted">{r.category}, {r.location}. Owner: {r.owner_name}</p>
        {r.photo_url && <img className="hero" src={fileUrl(r.photo_url)} alt={r.name} />}
        <p>{r.description}</p>
        <h2>Rules</h2><p>{r.rules || "No special rules."}</p>
        <h2>Who can book</h2>
        <ul>
          {r.requires_verification && <li>Verified identity</li>}
          {r.required_qualification && <li>Verified qualification: {r.required_qualification}</li>}
          {!r.requires_verification && !r.required_qualification && <li>Any signed-in user</li>}
        </ul>
        <h2>Price</h2><p>{money(r.price_per_hour)}{r.price_per_hour ? " per hour" : ""}</p>
        <h2>Booking slots</h2>
        {r.blocks.length > 0 && <p className="muted">Blocked: {r.blocks.map((b: Row) => `${new Date(b.start_time).toLocaleString()} (${b.reason})`).join("; ")}</p>}
        <label>Date<input type="date" value={day} min={today()} onChange={(e) => setDay(e.target.value)} /></label>
        <AvailabilityCalendar resourceId={r.id} day={day} onSelect={(s, e) => setSel([s, e])} />
        <button className="btn" disabled={!sel} onClick={() => nav(`/resources/${r.id}/book?start=${sel![0]}&end=${sel![1]}`)}>Request this time</button>
      </>
    )}</Async>
  );
}
