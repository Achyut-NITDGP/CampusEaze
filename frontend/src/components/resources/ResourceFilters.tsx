import { useSubmit } from "../../hooks/useSubmit";

export default function ResourceFilters({ onApply }: { onApply: (p: Record<string, string>) => void }) {
  const { onSubmit } = useSubmit(async (v) => onApply(v));
  return (
    <form className="filters" onSubmit={onSubmit} aria-label="Filter resources">
      <label>Search<input name="q" type="search" /></label>
      <label>Category
        <select name="category"><option value="">All</option><option value="equipment">Equipment</option><option value="space">Space</option><option value="service">Service</option></select>
      </label>
      <label>Location<input name="location" /></label>
      <label>Max price per hour<input name="max_price" type="number" min="0" /></label>
      <label>Free on<input name="day" type="date" /></label>
      <button className="btn">Apply filters</button>
    </form>
  );
}
