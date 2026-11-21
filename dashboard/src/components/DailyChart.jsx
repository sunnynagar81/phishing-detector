import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const tip = {
  background: "#121829", border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 10, color: "#eef1f8", fontSize: 12,
};

export default function DailyChart({ daily }) {
  if (!daily || daily.length === 0) {
    return <p className="muted">No scans in the last 14 days yet.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={270}>
      <BarChart data={daily} barSize={22}>
        <CartesianGrid stroke="rgba(255,255,255,0.07)" vertical={false} />
        <XAxis dataKey="date" stroke="#8d97ad" fontSize={11} tickLine={false} axisLine={false} />
        <YAxis allowDecimals={false} stroke="#8d97ad" fontSize={11} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tip} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
        <Bar dataKey="safe" stackId="a" fill="#22c55e" />
        <Bar dataKey="suspicious" stackId="a" fill="#fbbf24" />
        <Bar dataKey="dangerous" stackId="a" fill="#f43f5e" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}