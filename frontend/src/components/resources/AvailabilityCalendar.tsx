import { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Row } from "../../types";

export default function AvailabilityCalendar({ resourceId, day, onSelect }: { resourceId: number; day: string; onSelect: (s: string, e: string) => void }) {
  const { data } = useApi<Row[]>(`/resources/${resourceId}/slots?day=${day}`);
  const [sel, setSel] = useState<[number, number] | null>(null);
  useEffect(() => setSel(null), [day]);
  if (!data) return <p aria-busy="true">Loading slots…</p>;
  const click = (i: number) => {
    const n: [number, number] = sel && i === sel[1] + 1 ? [sel[0], i] : [i, i];
    setSel(n);
    onSelect(data[n[0]].start, data[n[1]].end);
  };
  return (
    <div className="slots" role="group" aria-label="Hourly slots. Select one hour, then the next hour to extend.">
      {data.map((s, i) => {
        const on = !!sel && i >= sel[0] && i <= sel[1];
        const t = new Date(s.start).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
        return (
          <button type="button" key={s.start} className={`slot ${s.available ? "" : "taken"} ${on ? "on" : ""}`} aria-pressed={on} onClick={() => click(i)}>
            {t}<small>{s.available ? "free" : "taken: join waiting list"}</small>
          </button>
        );
      })}
    </div>
  );
}
