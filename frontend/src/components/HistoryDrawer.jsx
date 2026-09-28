import React from "react";
import { X, History, ShieldAlert, ShieldCheck, AlertTriangle, ArrowRight, RefreshCw } from "lucide-react";

export default function HistoryDrawer({
  isOpen,
  onClose,
  historyItems,
  onRefreshHistory,
  onSelectHistoryItem,
  t
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        onClick={onClose}
        className="absolute inset-0 bg-slate-950/75 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-slate-800 p-6 flex flex-col shadow-2xl">
          
          {/* Header */}
          <div className="flex items-center justify-between pb-5 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <History className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-white tracking-tight">
                {t.navHistory}
              </h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                {historyItems.length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onRefreshHistory}
                className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                title="Refresh history"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={onClose}
                className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto py-4 space-y-3">
            {historyItems.length === 0 ? (
              <div className="text-center py-16 text-slate-500">
                <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No analysis history recorded yet.</p>
                <p className="text-xs text-slate-600 mt-1">Scan a message to save results locally.</p>
              </div>
            ) : (
              historyItems.map((item) => {
                const isScam = item.verdict === "SCAM";
                const isSafe = item.verdict === "LIKELY_SAFE";
                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      onSelectHistoryItem(item);
                      onClose();
                    }}
                    className="p-3.5 rounded-2xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 cursor-pointer transition-all hover:bg-slate-950 space-y-2 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                        isScam
                          ? "bg-red-500/20 text-red-400 border border-red-500/30"
                          : isSafe
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                      }`}>
                        {item.verdict}
                      </span>
                      <span className="text-[11px] text-slate-500 font-mono">
                        Score: <strong className={isScam ? "text-red-400" : isSafe ? "text-emerald-400" : "text-amber-400"}>{item.risk_score}</strong>/100
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 font-mono line-clamp-2">
                      {item.message_snippet}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>{t.categories?.[item.scam_category] || item.scam_category}</span>
                      <span className="flex items-center gap-1 text-slate-400 group-hover:text-amber-400 transition-colors">
                        View
                        <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
