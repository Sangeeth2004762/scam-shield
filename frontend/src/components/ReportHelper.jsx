import React, { useState } from "react";
import { 
  FileText, 
  Copy, 
  Check, 
  PhoneCall, 
  ExternalLink, 
  ShieldAlert, 
  SendHorizontal,
  Info 
} from "lucide-react";
import confetti from "canvas-confetti";

export default function ReportHelper({ reportDraft, t }) {
  const [copied, setCopied] = useState(false);

  if (!reportDraft) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(reportDraft.full_complaint_text);
    setCopied(true);
    try {
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.8 }
      });
    } catch (e) {
      // Confetti fallback
    }
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="bg-slate-900/90 border border-red-500/30 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden">
      
      {/* Ambient header flare */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-red-400 mb-1">
            <ShieldAlert className="w-4 h-4" />
            <span>Cybercrime Action Ready</span>
          </div>
          <h3 className="text-xl font-bold text-white tracking-tight">
            {t.reportHeader}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            {t.reportSub}
          </p>
        </div>

        {/* Copy Button */}
        <button
          type="button"
          onClick={handleCopy}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md ${
            copied
              ? "bg-emerald-600 text-white shadow-emerald-600/30 scale-105"
              : "bg-red-600 hover:bg-red-500 text-white shadow-red-600/25 hover:shadow-red-600/40"
          }`}
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              <span>{t.btnCopied}</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>{t.btnCopyReport}</span>
            </>
          )}
        </button>
      </div>

      {/* Monospace Formatted Draft Content */}
      <div className="mt-6 relative">
        <div className="p-4 sm:p-5 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto max-h-72 select-all shadow-inner">
          <pre className="whitespace-pre-wrap font-mono">
            {reportDraft.full_complaint_text}
          </pre>
        </div>
      </div>

      {/* Official Government Quick Actions */}
      <div className="mt-6 flex flex-wrap items-center gap-3">
        {/* Call 1930 Helpline */}
        <a
          href="tel:1930"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-red-500/15 border border-red-500/40 text-red-300 hover:bg-red-600 hover:text-white text-xs font-bold transition-all shadow-sm"
        >
          <PhoneCall className="w-4 h-4 animate-pulse" />
          <span>{t.btnCall1930}</span>
        </a>

        {/* National Cyber Crime Reporting Portal */}
        <a
          href="https://cybercrime.gov.in"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold transition-all"
        >
          <ExternalLink className="w-4 h-4 text-slate-400" />
          <span>{t.btnGovPortal}</span>
        </a>

        {/* Sanchar Saathi / Chakshu Portal (DoT) */}
        <a
          href="https://sancharsaathi.gov.in/sfc/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold transition-all"
        >
          <SendHorizontal className="w-4 h-4 text-slate-400" />
          <span>{t.btnChakshu}</span>
        </a>
      </div>

      {/* Official Notice / Disclaimer */}
      <div className="mt-5 flex items-start gap-2.5 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400">
        <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
        <p className="leading-normal">
          {t.reportDisclaimer}
        </p>
      </div>

    </div>
  );
}
