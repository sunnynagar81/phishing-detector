import { Activity, ShieldAlert, ShieldCheck, TriangleAlert } from "lucide-react";

export default function StatCards({ stats }) {
  const total = stats.total || 0;
  const pct = (n) => (total ? Math.round(((n || 0) / total) * 100) + "%" : "0%");
  const items = [
    { label: "Total scans", value: stats.total, cls: "total", Icon: Activity, show: "" },
    { label: "Safe", value: stats.safe, cls: "safe", Icon: ShieldCheck, show: pct(stats.safe) },
    { label: "Suspicious", value: stats.suspicious, cls: "suspicious", Icon: TriangleAlert, show: pct(stats.suspicious) },
    { label: "Dangerous", value: stats.dangerous, cls: "dangerous", Icon: ShieldAlert, show: pct(stats.dangerous) },
  ];
  return (
    <div className="cards">
      {items.map(({ label, value, cls, Icon, show }) => (
        <div key={label} className={"stat " + cls}>
          <div className="stat-icon"><Icon size={20} /></div>
          <div className="stat-value">{value ?? 0}</div>
          <div className="stat-label"><span>{label}</span><span className="stat-pct">{show}</span></div>
        </div>
      ))}
    </div>
  );
}