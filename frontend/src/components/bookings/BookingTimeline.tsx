import { Row } from "../../types";
import { fmt } from "../../utils/format";

export default function BookingTimeline({ events }: { events: Row[] }) {
  return (
    <ol className="timeline">
      {events.map((e) => (
        <li key={e.id}><time dateTime={e.timestamp}>{fmt(e.timestamp)}</time> <strong>{e.action.replace(/[._]/g, " ")}</strong> by {e.actor_name}{e.detail && <span className="muted">: {e.detail}</span>}</li>
      ))}
    </ol>
  );
}
