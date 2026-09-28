import React from "react";
import { ShieldAlert, ShieldCheck, BarChart3, History, PhoneCall, Languages } from "lucide-react";

export default function Navbar({
  currentLang,
  onLangChange,
  activeView,
  onViewChange,
  onOpenHistory,
  t
}) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div 
          onClick={() => onViewChange("scanner")}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-red-500 to-rose-600 shadow-lg shadow-red-500/20 group-hover:scale-105 transition-transform duration-200">
            <ShieldAlert className="w-5 h-5 text-white" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-black tracking-tight text-white group-hover:text-amber-400 transition-colors">
                Scam Shield
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-red-500/20 text-red-400 border border-red-500/30 rounded-md">
                INDIA
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              {t.appTagline}
            </p>
          </div>
        </div>

        {/* Navigation & Controls */}
        <div className="flex items-center gap-2 sm:gap-4">
          
          {/* View switcher */}
          <nav className="flex items-center bg-slate-900 border border-slate-800 p-1 rounded-xl">
            <button
              onClick={() => onViewChange("scanner")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeView === "scanner"
                  ? "bg-gradient-to-r from-red-600 to-amber-600 text-white shadow-md shadow-red-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {t.navHome}
            </button>
            <button
              onClick={() => onViewChange("insights")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeView === "insights"
                  ? "bg-gradient-to-r from-red-600 to-amber-600 text-white shadow-md shadow-red-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>{t.navInsights}</span>
            </button>
          </nav>

          {/* History Drawer Trigger */}
          <button
            onClick={onOpenHistory}
            className="p-2 rounded-xl text-slate-400 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
            title={t.navHistory}
          >
            <History className="w-4 h-4" />
          </button>

          {/* Language Selector */}
          <div className="relative flex items-center bg-slate-900 border border-slate-800 rounded-xl px-2 py-1">
            <Languages className="w-3.5 h-3.5 text-slate-400 mr-1.5" />
            <select
              value={currentLang}
              onChange={(e) => onLangChange(e.target.value)}
              className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer font-medium"
            >
              <option value="en" className="bg-slate-900 text-white">English</option>
              <option value="ta" className="bg-slate-900 text-white">தமிழ் (Tamil)</option>
              <option value="hi" className="bg-slate-900 text-white">हिन्दी (Hindi)</option>
            </select>
          </div>

          {/* Emergency 1930 Helpline Button */}
          <a
            href="tel:1930"
            className="hidden md:flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-red-600/15 border border-red-500/40 text-red-400 hover:bg-red-600 hover:text-white text-xs font-semibold transition-all shadow-sm"
          >
            <PhoneCall className="w-3.5 h-3.5 animate-pulse" />
            <span>{t.callHelpline}</span>
          </a>

        </div>

      </div>
    </header>
  );
}
