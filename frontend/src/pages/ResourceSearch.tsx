import { useState } from "react";
import Async from "../components/common/Async";
import ResourceCard from "../components/resources/ResourceCard";
import ResourceFilters from "../components/resources/ResourceFilters";
import { useApi } from "../hooks/useApi";
import { Row } from "../types";

export default function ResourceSearch() {
  const [p, setP] = useState<Record<string, string>>({});
  const qs = new URLSearchParams(Object.entries(p).filter(([, v]) => v)).toString();
  const d = useApi<Row[]>(`/resources?${qs}`);
  return (
    <>
      <h1>Search resources</h1>
      <ResourceFilters onApply={setP} />
      <Async d={d}>{(rs) => rs.length ? <div className="grid">{rs.map((r) => <ResourceCard key={r.id} r={r} />)}</div> : <p>No resources match. Try fewer filters.</p>}</Async>
    </>
  );
}
