import { useState } from "react";
import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import { useApi } from "../../hooks/useApi";
import { Row } from "../../types";
import { fmt } from "../../utils/format";

export default function AuditLogs() {
  const [t, setT] = useState("");
  const d = useApi<Row[]>(`/admin/audit-logs${t ? `?entity_type=${t}` : ""}`);
  return (
    <>
      <h1>Activity history</h1>
      <label>Show<select value={t} onChange={(e) => setT(e.target.value)}><option value="">Everything</option>{["booking", "incident", "resource", "user"].map((x) => <option key={x} value={x}>{x}</option>)}</select></label>
      <Async d={d}>{(rows) => <DataTable rows={rows} cols={[
        ["When", (a) => fmt(a.timestamp)], ["Who", (a) => a.actor_name], ["Action", (a) => a.action.replace(/[._]/g, " ")], ["Record", (a) => `${a.entity_type} #${a.entity_id}`], ["Detail", (a) => a.detail || "-"],
      ]} />}</Async>
    </>
  );
}
