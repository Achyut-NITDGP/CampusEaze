import { Link, useParams, useSearchParams } from "react-router-dom";
import Async from "../components/common/Async";
import BookingForm from "../components/bookings/BookingForm";
import { useApi } from "../hooks/useApi";
import { fmt } from "../utils/format";

export default function Checkout() {
  const { id } = useParams();
  const [q] = useSearchParams();
  const r = useApi<any>(`/resources/${id}`);
  const el = useApi<{ ok: boolean; issues: string[] }>(`/eligibility/check?resource_id=${id}`);
  const start = q.get("start"), end = q.get("end");
  if (!start || !end) return <p>Pick a time on the <Link to={`/resources/${id}`}>resource page</Link> first.</p>;
  return (
    <>
      <h1>Booking request</h1>
      <Async d={r}>{(res) => (
        <>
          <p><strong>{res.name}</strong><br />{fmt(start)} to {fmt(end)}</p>
          <Async d={el}>{(e) => e.ok
            ? <p className="ok">You meet this resource's requirements.</p>
            : <div role="alert" className="err"><p>You cannot book this yet:</p><ul>{e.issues.map((i) => <li key={i}>{i}</li>)}</ul><Link to="/profile">Open your profile to submit documents</Link></div>}
          </Async>
          <BookingForm resource={res} start={start} end={end} />
        </>
      )}</Async>
    </>
  );
}
