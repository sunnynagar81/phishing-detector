import { Trash2 } from "lucide-react";

export default function HistoryTable({ rows, filters, setFilters, onClear }) {
  return (
    <div>
      <div className="filters">
        <select value={filters.scan_type}
                onChange={(e) => setFilters({ ...filters, scan_type: e.target.value })}>
          <option value="">All types</option>
          <option value="url">URL</option>
          <option value="sms">SMS</option>
          <option value="email">Email</option>
        </select>
        <select value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All results</option>
          <option value="safe">Safe</option>
          <option value="suspicious">Suspicious</option>
          <option value="dangerous">Dangerous</option>
        </select>
        <button className="danger" style={{ marginLeft: "auto" }} onClick={onClear}>
          <Trash2 size={15} /> Clear
        </button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Time</th><th>Type</th><th>Content</th><th>Result</th><th>Score</th></tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan="5" className="muted">No scans match.</td></tr>
            )}
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="time">{r.created_at ? new Date(r.created_at).toLocaleString() : ""}</td>
                <td><span className="chip">{r.scan_type}</span></td>
                <td className="content" title={r.content}>{r.content}</td>
                <td><span className={"badge " + r.status}>{r.status}</span></td>
                <td>
                  <span className={"mini-meter " + r.status}
                        style={{ "--tone": { safe: "#22c55e", suspicious: "#fbbf24", dangerous: "#f43f5e" }[r.status] }}>
                    <i style={{ width: Math.round(r.probability * 100) + "%" }} />
                  </span>
                  {Math.round(r.probability * 100)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}