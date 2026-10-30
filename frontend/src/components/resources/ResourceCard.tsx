import { Link } from "react-router-dom";
import { fileUrl } from "../../services/api";
import { Row } from "../../types";
import { money } from "../../utils/format";

export default function ResourceCard({ r }: { r: Row }) {
  return (
    <article className="card">
      <div className="thumb" role="img" aria-label={r.photo_url ? r.name : "No photo"} style={r.photo_url ? { backgroundImage: `url(${fileUrl(r.photo_url)})` } : undefined}>
        {!r.photo_url && <span className="tag">{r.category}</span>}
      </div>
      <h3><Link to={`/resources/${r.id}`}>{r.name}</Link></h3>
      <p className="muted">{r.location}</p>
      <p>{money(r.price_per_hour)}{r.price_per_hour ? " per hour" : ""}</p>
      {r.required_qualification && <span className="tag">Needs {r.required_qualification}</span>}
    </article>
  );
}
