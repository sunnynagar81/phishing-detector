import { Activity, History, PieChart, RefreshCw, ScanSearch, ShieldCheck } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { clearHistory, getHistory, getStats } from "./api";
import DailyChart from "./components/DailyChart";
import DonutChart from "./components/DonutChart";
import HistoryTable from "./components/HistoryTable";
import ScanBox from "./components/ScanBox";
import StatCards from "./components/StatCards";

export default function App() {
  const [stats, setStats] = useState({ total: 0, safe: 0, suspicious: 0, dangerous: 0, daily: [] });
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState({ scan_type: "", status: "" });
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [s, h] = await Promise.all([getStats(), getHistory(filters)]);
      setStats(s);
      setRows(h);
      setError("");
    } catch (e) {
      setError("Cannot load data. Check that the backend and MongoDB are running.");
    }
  }, [filters]);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 10000); // picks up scans made by the extension
    return () => clearInterval(id);
  }, [refresh]);

  async function handleClear() {
    if (!window.confirm("Delete all scan history?")) return;
    await clearHistory();
    refresh();
  }

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <div className="logo"><ShieldCheck size={26} color="#fff" /></div>
          <div>
            <h1>PhishGuard AI</h1>
            <p>Real-time phishing detection for URLs, SMS and email</p>
          </div>
        </div>
        <div className="top-actions">
          <div className="live"><span className="dot" />Live, updates every 10s</div>
          <button onClick={refresh}><RefreshCw size={15} /> Refresh</button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <StatCards stats={stats} />

      <div className="grid2">
        <section className="panel">
          <div className="panel-head"><h2><ScanSearch size={18} /> Scan something</h2></div>
          <ScanBox onDone={refresh} />
        </section>
        <section className="panel">
          <div className="panel-head"><h2><Activity size={18} /> Scans per day</h2>
            <span className="muted">Last 14 days</span></div>
          <DailyChart daily={stats.daily} />
        </section>
      </div>

      <div className="grid3">
        <section className="panel">
          <div className="panel-head"><h2><PieChart size={18} /> Breakdown</h2></div>
          <DonutChart stats={stats} />
        </section>
        <section className="panel">
          <div className="panel-head"><h2><History size={18} /> Scan history</h2></div>
          <HistoryTable rows={rows} filters={filters} setFilters={setFilters} onClear={handleClear} />
        </section>
      </div>
    </div>
  );
}