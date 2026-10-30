import { ReactNode } from "react";
import { Row } from "../../types";

export default function DataTable({ cols, rows, empty = "Nothing to show yet." }: { cols: [string, (r: Row) => ReactNode][]; rows: Row[]; empty?: string }) {
  if (!rows.length) return <p className="muted">{empty}</p>;
  return (
    <div className="scroll">
      <table>
        <thead><tr>{cols.map((c) => <th key={c[0]} scope="col">{c[0]}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={r.id ?? i}>{cols.map((c) => <td key={c[0]}>{c[1](r)}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}
