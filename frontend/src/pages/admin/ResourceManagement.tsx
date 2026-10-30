import { Link } from "react-router-dom";
import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import StatusBadge from "../../components/common/StatusBadge";
import { useApi } from "../../hooks/useApi";
import { Row } from "../../types";

export default function ResourceManagement() {
  const d = useApi<Row[]>("/resources/managed");
  return (
    <>
      <h1>Resource management</h1>
      <Link className="btn" to="/admin/resources/new">Add a resource</Link>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="You have not added any resources yet." cols={[
        ["Name", (r) => r.name], ["Type", (r) => r.category], ["Requires", (r) => r.required_qualification ?? (r.requires_verification ? "Verified identity" : "Nothing")],
        ["Status", (r) => <StatusBadge s={r.status} />], ["", (r) => <Link to={`/admin/resources/${r.id}/edit`}>Edit and block slots</Link>],
      ]} />}</Async>
    </>
  );
}
