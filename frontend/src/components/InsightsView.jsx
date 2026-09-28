import React, { useEffect, useState } from "react";
import { 
  BarChart3, 
  PieChart as PieIcon, 
  ShieldAlert, 
  ShieldCheck, 
  TrendingUp, 
  AlertOctagon, 
  Info, 
  ExternalLink,
  RefreshCw
} from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Legend 
} from "recharts";

const VERDICT_COLORS = {
  SCAM: "#ef4444",
  SUSPICIOUS: "#f59e0b",
  LIKELY_SAFE: "#10b981"
};

const CATEGORY_COLORS = [
  "#ef4444", "#f97316", "#f59e0b", "#eab308", 
  "#84cc16", "#10b981", "#06b6d4", "#3b82f6", 
  "#8b5cf6", "#ec4899"
];

export default function InsightsView({ t, apiUrl }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/stats`);
      if (!res.ok) throw new Error("Failed to load statistics");
      const data = await res.json();
      setStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [apiUrl]);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Title & Refresh */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <BarChart3 className="w-6 h-6 text-amber-400" />
            <span>{t.insightsTitle}</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            {t.insightsSub}
          </p>
        </div>
        <button
          type="button"
          onClick={fetchStats}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Intelligence</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        
        <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              {t.totalScans}
            </p>
            <h3 className="text-2xl font-black text-white mt-0.5">
              {stats?.total_scans ?? 0}
            </h3>
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 shrink-0">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              {t.highRiskScams}
            </p>
            <h3 className="text-2xl font-black text-red-400 mt-0.5">
              {stats?.high_risk_scam_count ?? 0}
            </h3>
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              {t.avgRisk}
            </p>
            <h3 className="text-2xl font-black text-white mt-0.5">
              {stats?.avg_risk_score ?? 0} <span className="text-xs font-normal text-slate-500">/ 100</span>
            </h3>
          </div>
        </div>

      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Scam Categories Bar Chart */}
        <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl">
          <h3 className="text-base font-bold text-white mb-1">
            {t.categoryBreakdown}
          </h3>
          <p className="text-xs text-slate-400 mb-6">Distribution across Indian cyber scam categories</p>
          
          <div className="h-64 w-full">
            {stats?.category_distribution && stats.category_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.category_distribution} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <XAxis type="number" stroke="#64748b" fontSize={11} />
                  <YAxis type="category" dataKey="category" stroke="#64748b" fontSize={10} width={90} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                    formatter={(val, name, props) => [`${val} (${props.payload.percentage}%)`, "Scans"]}
                  />
                  <Bar dataKey="count" radius={[0, 8, 8, 0]}>
                    {stats.category_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                Scan more messages to populate category distribution
              </div>
            )}
          </div>
        </div>

        {/* Verdict Distribution Pie Chart */}
        <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl">
          <h3 className="text-base font-bold text-white mb-1">
            {t.verdictDistribution}
          </h3>
          <p className="text-xs text-slate-400 mb-6">Proportion of Confirmed Scam vs Suspicious vs Likely Safe</p>
          
          <div className="h-64 w-full">
            {stats?.verdict_distribution && stats.verdict_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.verdict_distribution}
                    dataKey="count"
                    nameKey="verdict"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={85}
                    paddingAngle={4}
                  >
                    {stats.verdict_distribution.map((entry, index) => (
                      <Cell key={`pie-${index}`} fill={VERDICT_COLORS[entry.verdict] || "#64748b"} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                    formatter={(val, name, props) => [`${val} scans (${props.payload.percentage}%)`, name]}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36} 
                    formatter={(val) => <span className="text-xs text-slate-300 font-medium">{val}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                Scan more messages to populate verdict distribution
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Cyber Threat Briefing on Trending Indian Scam Vectors */}
      <div className="bg-slate-900/90 border border-slate-800 p-6 sm:p-8 rounded-3xl shadow-xl space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            <span>{t.threatBriefingTitle}</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Field threat advisory based on reports from Indian Cyber Crime Coordination Centre (I4C) & NPCI
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30 uppercase">
              Extortion Vector
            </span>
            <h4 className="text-sm font-bold text-white">1. "Digital Arrest" Video Call Intimidation</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Scammers pose as CBI or Mumbai Police officers over Skype/WhatsApp video calls with fake police backdrops. They claim a parcel with narcotics was sent using the victim's Aadhaar.
            </p>
            <p className="text-[11px] text-amber-400 font-medium">
              💡 Truth: There is NO concept of "Digital Arrest" under the Bharatiya Nagarik Suraksha Sanhita (BNSS) or Indian law. Police never conduct trials on Skype.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 uppercase">
              Utility Vector
            </span>
            <h4 className="text-sm font-bold text-white">2. Electricity Bill Disconnection Panic</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Victims receive an SMS stating their power supply will be cut off at 9:30 PM tonight due to an unpaid bill, urging them to call a mobile number. The fraudster instructs them to install a remote desktop app (AnyDesk/TeamViewer).
            </p>
            <p className="text-[11px] text-amber-400 font-medium">
              💡 Truth: Electricity distribution companies (DISCOMs/TNEB) never send disconnection threats from personal 10-digit mobile numbers with immediate night deadlines.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30 uppercase">
              Ponzi Vector
            </span>
            <h4 className="text-sm font-bold text-white">3. YouTube Review & Telegram Tasks</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Victims are paid Rs. 150-500 for liking a few YouTube videos or rating Google hotels. Once trust is gained, they are added to a Telegram group and asked to make "crypto deposits" for massive returns, locking their funds.
            </p>
            <p className="text-[11px] text-amber-400 font-medium">
              💡 Truth: Legitimate companies never pay daily returns for simple social media likes or require advance security deposits.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30 uppercase">
              Financial Vector
            </span>
            <h4 className="text-sm font-bold text-white">4. UPI Collect "Reverse Cashback" Scam</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Scammers send a collect request on PhonePe, Google Pay, or Paytm claiming it is an approved refund or reward. They tell the victim to enter their UPI PIN to "receive" the money.
            </p>
            <p className="text-[11px] text-amber-400 font-medium">
              💡 Truth: Entering your UPI PIN ALWAYS DEDUCTS money from your bank account. You NEVER need to enter a UPI PIN to receive money.
            </p>
          </div>

        </div>
      </div>

    </div>
  );
}
