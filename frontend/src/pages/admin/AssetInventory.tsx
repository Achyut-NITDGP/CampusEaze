import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import StatusBadge from "../../components/common/StatusBadge";
import { useApi } from "../../hooks/useApi";
import { Row } from "../../types";
import { fmt, money } from "../../utils/format";

export default function AssetInventory() {
  const d = useApi<Row[]>("/admin/inventory");
  return (
    <>
      <h1>Asset inventory</h1>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="No resources yet." cols={[
        ["Name", (r) => r.name], ["Type", (r) => r.category], ["Location", (r) => r.location], ["Price", (r) => money(r.price_per_hour)],
        ["Status", (r) => <StatusBadge s={r.current_status} />], ["In use by", (r) => r.current_user ?? "-"], ["Next booking", (r) => r.next_booking ? fmt(r.next_booking) : "-"],
      ]} />}</Async>
    </>
  );
}
