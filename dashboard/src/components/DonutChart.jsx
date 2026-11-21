import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = { safe: "#22c55e", suspicious: "#fbbf24", dangerous: "#f43f5e" };

export default function DonutChart({ stats }) {
  const data = ["safe", "suspicious", "dangerous"].map((k) => ({ name: k, value: stats[k] || 0 }));
  const total = stats.total || 0;

  if (total === 0) return <p className="muted">Scan something to see the breakdown.</p>;

  return (
    <div>
      <div style={{ position: "relative", height: 190 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" innerRadius={58} outerRadius={82} paddingAngle={3} stroke="none">
              {data.map((d) => <Cell key={d.name} fill={COLORS[d.name]} />)}
            </Pie>
            <Tooltip contentStyle={{ background: "#121829", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 10, color: "#eef1f8", fontSize: 12 }} />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", pointerEvents: "none", textAlign: "center" }}>
          <div>
            <div style={{ fontSize: 26, fontWeight: 800 }}>{total}</div>
            <div className="muted" style={{ fontSize: 11 }}>total</div>
          </div>
        </div>
      </div>
      <div className="legend">
        {data.map((d) => (
          <div key={d.name}>
            <span className="k"><i style={{ background: COLORS[d.name] }} />{d.name[0].toUpperCase() + d.name.slice(1)}</span>
            <strong>{d.value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}