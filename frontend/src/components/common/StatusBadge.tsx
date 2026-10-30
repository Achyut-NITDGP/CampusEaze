export default function StatusBadge({ s }: { s: string }) {
  return <span className={`badge ${s}`}>{s.replace("_", " ")}</span>;
}
