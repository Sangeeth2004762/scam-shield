import React, { useState } from "react";
import { X, Sparkles, ShieldCheck, ShieldAlert, AlertTriangle, ArrowRight } from "lucide-react";
import { DEMO_EXAMPLES } from "../data/demoExamples";

export default function DemoModal({ isOpen, onClose, onSelectExample, t }) {
  const [filter, setFilter] = useState("ALL");

  if (!isOpen) return null;

  const filteredExamples = DEMO_EXAMPLES.filter((ex) => {
    if (filter === "ALL") return true;
    if (filter === "GENUINE") return ex.expectedVerdict === "LIKELY_SAFE";
    if (filter === "BANKING") return ex.category === "KYC_BANK" || ex.category === "UPI_COLLECT" || ex.category === "LOAN_APP";
    if (filter === "EXTORTION") return ex.category === "DIGITAL_ARREST" || ex.category === "UTILITY_BILL" || ex.category === "PARCEL_COURIER";
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">
                {t.btnExamples}
              </h3>
              <p className="text-xs text-slate-400">
                Select from 8 realistic Indian scam vectors or 2 genuine messages to test accuracy
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Pills */}
        <div className="px-6 py-3 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto shrink-0">
          {[
            { id: "ALL", label: "All (10)" },
            { id: "BANKING", label: "Banking & UPI (3)" },
            { id: "EXTORTION", label: "Digital Arrest & Threat (3)" },
            { id: "GENUINE", label: "Genuine / Safe (2)" }
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                filter === f.id
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                  : "bg-slate-950 text-slate-400 border border-slate-800 hover:text-slate-200"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Cards Grid */}
        <div className="p-6 overflow-y-auto space-y-3.5">
          {filteredExamples.map((ex) => {
            const isSafe = ex.expectedVerdict === "LIKELY_SAFE";
            return (
              <div
                key={ex.id}
                onClick={() => {
                  onSelectExample(ex);
                  onClose();
                }}
                className={`p-4 rounded-2xl border transition-all cursor-pointer group flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                  isSafe
                    ? "bg-emerald-950/20 border-emerald-500/30 hover:border-emerald-500/60 hover:bg-emerald-950/30"
                    : "bg-slate-950/70 border-slate-800 hover:border-amber-500/50 hover:bg-slate-950"
                }`}
              >
                <div className="space-y-1.5 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                      isSafe
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-red-500/20 text-red-400 border border-red-500/30"
                    }`}>
                      {ex.badge}
                    </span>
                    <h4 className="text-sm font-bold text-white group-hover:text-amber-400 transition-colors">
                      {ex.title}
                    </h4>
                  </div>
                  <p className="text-xs text-slate-300 font-mono line-clamp-2 bg-slate-900/60 p-2 rounded-lg border border-slate-800/80">
                    "{ex.text}"
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Sender: <span className="text-slate-400 font-medium">{ex.sender}</span> • {ex.description}
                  </p>
                </div>

                <button
                  type="button"
                  className="shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 group-hover:bg-amber-500 group-hover:text-slate-950 text-xs font-bold text-slate-200 transition-all shadow-sm"
                >
                  <span>Load</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
