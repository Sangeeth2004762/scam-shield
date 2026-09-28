import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import InputCard from "./components/InputCard";
import ResultCard from "./components/ResultCard";
import ReportHelper from "./components/ReportHelper";
import DemoModal from "./components/DemoModal";
import HistoryDrawer from "./components/HistoryDrawer";
import InsightsView from "./components/InsightsView";
import { TRANSLATIONS } from "./data/translations";
import { AlertCircle, ShieldAlert, Sparkles, CheckCircle, ChevronDown, ArrowDown } from "lucide-react";

// Use relative API path or configurable env URL
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [currentLang, setCurrentLang] = useState("en"); // "en" | "ta" | "hi"
  const [activeView, setActiveView] = useState("scanner"); // "scanner" | "insights"
  const [historyOpen, setHistoryOpen] = useState(false);
  const [demoOpen, setDemoOpen] = useState(false);

  // Input states
  const [text, setText] = useState("");
  const [sender, setSender] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [saveHistory, setSaveHistory] = useState(true);

  // Analysis states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [historyItems, setHistoryItems] = useState([]);

  const t = TRANSLATIONS[currentLang] || TRANSLATIONS.en;

  // Load history on mount
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/history?limit=25`);
      if (res.ok) {
        const data = await res.json();
        setHistoryItems(data.items || []);
      }
    } catch (e) {
      console.warn("Could not load scan history:", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // When language changes, if result already exists and user wants text translated, they can re-scan or we pass lang
  const handleLangChange = (newLang) => {
    setCurrentLang(newLang);
    // If there is already an analyzed text, user can click scan again to see response in that language
  };

  const handleClear = () => {
    setText("");
    setSender("");
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  const handleSelectExample = (example) => {
    setText(example.text);
    setSender(example.sender || "");
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  const handleSelectHistoryItem = (item) => {
    setText(item.message_snippet || "");
    setSender(item.sender || "");
    setSelectedFile(null);
    setResult({
      id: item.id,
      verdict: item.verdict,
      risk_score: item.risk_score,
      rule_score: item.risk_score,
      llm_score: item.risk_score,
      scam_category: item.scam_category,
      red_flags: item.red_flags || [],
      explanation: item.explanation || "",
      what_to_do: item.what_to_do || [],
      confidence: item.confidence || 0.9,
      entities: { urls: [], phones: [], upi_ids: [], amounts: [] },
      rule_findings: [],
      language: item.language,
      model_used: "Historical Record",
      analyzed_at: item.created_at
    });
    setActiveView("scanner");
  };

  const handleAnalyze = async (mode = "text") => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let res;
      if (mode === "text") {
        if (!text.trim()) {
          throw new Error("Please enter or paste a message to analyze.");
        }
        res = await fetch(`${API_URL}/api/analyze/text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: text.trim(),
            sender: sender.trim() || null,
            language: currentLang,
            save_history: saveHistory
          })
        });
      } else {
        if (!selectedFile) {
          throw new Error("Please select or drop a screenshot image to analyze.");
        }
        const formData = new FormData();
        formData.append("file", selectedFile);
        if (sender.trim()) formData.append("sender", sender.trim());
        formData.append("language", currentLang);
        formData.append("save_history", String(saveHistory));

        res = await fetch(`${API_URL}/api/analyze/image`, {
          method: "POST",
          body: formData
        });
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error (${res.status})`);
      }

      const data = await res.json();
      setResult(data);
      fetchHistory(); // Refresh history drawer in background

      // Smooth scroll to results
      setTimeout(() => {
        const resultElement = document.getElementById("results-section");
        if (resultElement) {
          resultElement.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, 100);

    } catch (err) {
      setError(err.message || "Failed to analyze message. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-amber-500/30 selection:text-amber-200">
      
      {/* Navigation */}
      <Navbar
        currentLang={currentLang}
        onLangChange={handleLangChange}
        activeView={activeView}
        onViewChange={setActiveView}
        onOpenHistory={() => setHistoryOpen(true)}
        t={t}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {activeView === "scanner" ? (
          <div className="space-y-10 max-w-4xl mx-auto">
            
            {/* Hero / Intro */}
            <div className="text-center space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Multi-modal Cyber Defense for India</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
                {t.appTitle}
              </h1>
              <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
                {t.appSub}
              </p>
            </div>

            {/* Input Card */}
            <InputCard
              text={text}
              setText={setText}
              sender={sender}
              setSender={setSender}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              saveHistory={saveHistory}
              setSaveHistory={setSaveHistory}
              onAnalyze={handleAnalyze}
              onOpenDemo={() => setDemoOpen(true)}
              onClear={handleClear}
              loading={loading}
              t={t}
            />

            {/* Error Banner */}
            {error && (
              <div className="p-4 rounded-2xl bg-red-950/60 border border-red-500/40 flex items-start gap-3 text-red-200 text-sm animate-in fade-in">
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-red-300">Analysis Error</h4>
                  <p className="mt-0.5 text-xs text-red-200/80">{error}</p>
                </div>
              </div>
            )}

            {/* Results Section */}
            {result && (
              <div id="results-section" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <ResultCard
                  result={result}
                  t={t}
                  currentLang={currentLang}
                />

                {/* Pre-filled Report Helper for SCAM / SUSPICIOUS */}
                {result.report_draft && (
                  <ReportHelper
                    reportDraft={result.report_draft}
                    t={t}
                  />
                )}
              </div>
            )}

          </div>
        ) : (
          <div className="max-w-5xl mx-auto">
            <InsightsView t={t} apiUrl={API_URL} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-8 text-xs text-slate-500 text-center">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-medium text-slate-400">
            Scam Shield — Digital Safety & Cybersecurity Hackathon Entry
          </p>
          <p>
            Powered by Google Gemini Flash & Deterministic Indian Threat Rules • Integrated with Cybercrime Helpline 1930 & Chakshu
          </p>
          <p className="text-[11px] text-slate-600">
            Disclaimer: Scam Shield assists in risk identification and report drafting. It does not replace official police FIRs or formal legal recourse.
          </p>
        </div>
      </footer>

      {/* Modals & Drawers */}
      <DemoModal
        isOpen={demoOpen}
        onClose={() => setDemoOpen(false)}
        onSelectExample={handleSelectExample}
        t={t}
      />

      <HistoryDrawer
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
        historyItems={historyItems}
        onRefreshHistory={fetchHistory}
        onSelectHistoryItem={handleSelectHistoryItem}
        t={t}
      />

    </div>
  );
}
