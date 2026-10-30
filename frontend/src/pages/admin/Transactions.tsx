import Async from "../../components/common/Async";
import DataTable from "../../components/common/DataTable";
import StatusBadge from "../../components/common/StatusBadge";
import { useApi } from "../../hooks/useApi";
import { Row } from "../../types";
import { fmt, money } from "../../utils/format";

export default function Transactions() {
  const d = useApi<Row[]>("/admin/transactions");
  return (
    <>
      <h1>Transactions</h1>
      <p className="muted">Payments are simulated in this prototype. Refunds appear when a paid request is rejected or cancelled.</p>
      <Async d={d}>{(rows) => <DataTable rows={rows} empty="No paid bookings yet." cols={[
        ["Receipt", (r) => r.receipt], ["User", (r) => r.user], ["Resource", (r) => r.resource], ["Amount", (r) => money(r.amount)],
        ["Status", (r) => <StatusBadge s={r.payment_status} />], ["Date", (r) => fmt(r.created_at)],
      ]} />}</Async>
    </>
  );
}
