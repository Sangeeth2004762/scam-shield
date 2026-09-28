import React from "react";
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  ExternalLink, 
  Phone, 
  CreditCard, 
  Link as LinkIcon, 
  Cpu, 
  Layers, 
  Eye,
  CheckCircle,
  HelpCircle
} from "lucide-react";

export default function ResultCard({ result, t, currentLang }) {
  if (!result) return null;

  const {
    verdict,
    risk_score,
    rule_score,
    llm_score,
    scam_category,
    red_flags,
    explanation,
    what_to_do,
    confidence,
    entities,
    ocr_extracted_text,
    model_used
  } = result;

  // Visual style config based on verdict
  const isScam = verdict === "SCAM";
  const isSuspicious = verdict === "SUSPICIOUS";
  const isSafe = verdict === "LIKELY_SAFE";

  const theme = isScam
    ? {
        border: "border-red-500/40",
        bg: "bg-red-500/10",
        text: "text-red-400",
        badgeBg: "bg-red-500/20 text-red-300 border-red-500/40",
        gaugeColor: "#ef4444",
        glow: "shadow-red-500/10",
        icon: ShieldAlert,
        verdictText: t.verdictScam
      }
    : isSuspicious
    ? {
        border: "border-amber-500/40",
        bg: "bg-amber-500/10",
        text: "text-amber-400",
        badgeBg: "bg-amber-500/20 text-amber-300 border-amber-500/40",
        gaugeColor: "#f59e0b",
        glow: "shadow-amber-500/10",
        icon: AlertTriangle,
        verdictText: t.verdictSuspicious
      }
    : {
        border: "border-emerald-500/40",
        bg: "bg-emerald-500/10",
        text: "text-emerald-400",
        badgeBg: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
        gaugeColor: "#10b981",
        glow: "shadow-emerald-500/10",
        icon: ShieldCheck,
        verdictText: t.verdictSafe
      };

  const VerdictIcon = theme.icon;
  const categoryLabel = t.categories?.[scam_category] || scam_category;

  // Circular gauge math (radius 42, circumference ~264)
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (risk_score / 100) * circumference;

  return (
    <div className={`bg-slate-900/90 border ${theme.border} rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl transition-all duration-300`}>
      
      {/* Top Banner: Verdict & Gauge */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
        
        {/* Left: Verdict info */}
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <span className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-black tracking-wide border ${theme.badgeBg}`}>
              <VerdictIcon className="w-4 h-4" />
              {theme.verdictText}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
              {categoryLabel}
            </span>
          </div>

          <div>
            <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {isScam ? "Immediate Caution Required" : isSuspicious ? "Unverified / High Risk Factors" : "Safe Transactional Alert"}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
              <Cpu className="w-3.5 h-3.5 text-slate-500" />
              <span>Model: <strong className="text-slate-300">{model_used}</strong></span>
              <span>•</span>
              <span>Confidence: <strong className="text-slate-300">{(confidence * 100).toFixed(0)}%</strong></span>
            </p>
          </div>
        </div>

        {/* Right: Circular Risk Meter */}
        <div className="flex items-center gap-5 self-center sm:self-auto bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
          <div className="relative w-24 h-24 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
              {/* Background circle */}
              <circle
                cx="50"
                cy="50"
                r={radius}
                stroke="#1e293b"
                strokeWidth="10"
                fill="none"
              />
              {/* Progress meter */}
              <circle
                cx="50"
                cy="50"
                r={radius}
                stroke={theme.gaugeColor}
                strokeWidth="10"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className={`text-2xl font-black ${theme.text}`}>
                {risk_score}
              </span>
              <span className="text-[10px] uppercase font-bold text-slate-500 -mt-1">
                Risk / 100
              </span>
            </div>
          </div>

          {/* Sub Scores */}
          <div className="space-y-1.5 text-xs text-slate-400">
            <div className="flex items-center justify-between gap-4">
              <span className="text-slate-500">{t.ruleScoreLabel}:</span>
              <span className="font-semibold text-slate-200">{rule_score}/100</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-slate-500">{t.llmScoreLabel}:</span>
              <span className="font-semibold text-slate-200">{llm_score}/100</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-slate-500">{t.confidenceLabel}:</span>
              <span className="font-semibold text-emerald-400">{(confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

      </div>

      {/* OCR Text Box (if screenshot was uploaded) */}
      {ocr_extracted_text && (
        <div className="mt-6 p-4 rounded-2xl bg-slate-950 border border-slate-800">
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 mb-1.5">
            <Eye className="w-4 h-4" />
            <span>{t.extractedTextTitle}</span>
          </div>
          <p className="text-xs text-slate-300 font-mono whitespace-pre-wrap line-clamp-3">
            {ocr_extracted_text}
          </p>
        </div>
      )}

      {/* Plain Language Explanation */}
      <div className="mt-6 p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80">
        <h4 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <span>{t.explanationTitle}</span>
        </h4>
        <p className="text-sm text-slate-300 leading-relaxed font-sans">
          {explanation}
        </p>
      </div>

      {/* Detected Red Flags & Heuristics */}
      {red_flags && red_flags.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>{t.redFlagsTitle}</span>
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {red_flags.map((flag, idx) => (
              <div 
                key={idx}
                className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-950/50 border border-slate-800 text-xs text-slate-300"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 shrink-0" />
                <span>{flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Entities Checklist */}
      {entities && (entities.urls?.length > 0 || entities.phones?.length > 0 || entities.upi_ids?.length > 0 || entities.amounts?.length > 0) && (
        <div className="mt-6 p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            {t.entitiesFoundTitle}
          </h4>
          <div className="flex flex-wrap gap-2 text-xs">
            {entities.urls?.map((url, i) => (
              <span key={`url-${i}`} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 text-amber-300 border border-slate-700 font-mono">
                <LinkIcon className="w-3 h-3" />
                {url}
              </span>
            ))}
            {entities.phones?.map((phone, i) => (
              <span key={`p-${i}`} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 text-sky-300 border border-slate-700 font-mono">
                <Phone className="w-3 h-3" />
                +91 {phone}
              </span>
            ))}
            {entities.upi_ids?.map((upi, i) => (
              <span key={`u-${i}`} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 text-purple-300 border border-slate-700 font-mono">
                <CreditCard className="w-3 h-3" />
                {upi}
              </span>
            ))}
            {entities.amounts?.map((amt, i) => (
              <span key={`a-${i}`} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 text-emerald-300 border border-slate-700 font-mono font-bold">
                {amt}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action Steps: What To Do Right Now */}
      {what_to_do && what_to_do.length > 0 && (
        <div className="mt-6 p-5 rounded-2xl bg-slate-950/80 border border-slate-800">
          <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{t.actionTitle}</span>
          </h4>
          <ol className="space-y-2.5 text-xs sm:text-sm text-slate-300">
            {what_to_do.map((step, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold shrink-0 mt-0.5 border border-emerald-500/30">
                  {idx + 1}
                </span>
                <span className="leading-relaxed">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

    </div>
  );
}
