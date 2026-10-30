import { Link } from "react-router-dom";
import Async from "../components/common/Async";
import StatusBadge from "../components/common/StatusBadge";
import ResourceCard from "../components/resources/ResourceCard";
import { useAuth } from "../contexts/AuthContext";
import { useApi } from "../hooks/useApi";
import { Row } from "../types";
import { fmt } from "../utils/format";

function List({ rows }: { rows: Row[] }) {
  if (!rows.length) return <p className="muted">Nothing here yet.</p>;
  return <ul className="list">{rows.map((b) => <li key={b.id}><Link to={`/bookings/${b.id}`}>{b.resource_name}</Link>, {fmt(b.start_time)} <StatusBadge s={b.status} /></li>)}</ul>;
}

export default function Home() {
  const { user } = useAuth();
  const d = useApi<Row>("/users/me/dashboard");
  return (
    <>
      <h1>Welcome, {user?.name}</h1>
      <Async d={d}>{(x) => (
        <>
          <p><Link to="/notifications">{x.unread} unread notification{x.unread === 1 ? "" : "s"}</Link></p>
          <section aria-labelledby="up"><h2 id="up">Upcoming bookings</h2><List rows={x.upcoming} /></section>
          <section aria-labelledby="pe"><h2 id="pe">Pending requests</h2><List rows={x.pending} /></section>
          <section aria-labelledby="rc">
            <h2 id="rc">Suggested for you</h2>
            <p className="muted">Matched from your past bookings and verified qualifications. A suggestion never grants access.</p>
            <div className="grid">{x.recommended.map((r: Row) => <ResourceCard key={r.id} r={r} />)}</div>
          </section>
        </>
      )}</Async>
    </>
  );
}
