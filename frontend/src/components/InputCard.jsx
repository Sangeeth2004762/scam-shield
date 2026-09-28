import React, { useState, useRef } from "react";
import { 
  FileText, 
  UploadCloud, 
  Sparkles, 
  X, 
  ShieldAlert, 
  Lock, 
  AlertCircle, 
  ArrowRight,
  Image as ImageIcon 
} from "lucide-react";

export default function InputCard({
  text,
  setText,
  sender,
  setSender,
  selectedFile,
  setSelectedFile,
  saveHistory,
  setSaveHistory,
  onAnalyze,
  onOpenDemo,
  onClear,
  loading,
  t
}) {
  const [activeTab, setActiveTab] = useState("text"); // "text" | "image"
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("image/")) {
        setSelectedFile(file);
        setActiveTab("image");
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const canSubmit = activeTab === "text" 
    ? text.trim().length >= 3 
    : selectedFile !== null;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden">
      {/* Decorative ambient gradient */}
      <div className="absolute top-0 right-0 -mt-12 -mr-12 w-64 h-64 bg-gradient-to-br from-amber-500/10 via-red-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>{t.inputHeader}</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          {t.inputSub}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 mb-6 gap-6">
        <button
          type="button"
          onClick={() => setActiveTab("text")}
          className={`flex items-center gap-2 pb-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === "text"
              ? "border-amber-500 text-amber-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>{t.textTab}</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("image")}
          className={`flex items-center gap-2 pb-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === "image"
              ? "border-amber-500 text-amber-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <ImageIcon className="w-4 h-4" />
          <span>{t.uploadTab}</span>
          {selectedFile && (
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          )}
        </button>
      </div>

      {/* Input Body */}
      {activeTab === "text" ? (
        <div className="space-y-4">
          <div className="relative">
            <textarea
              rows={5}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t.pastePlaceholder}
              className="w-full bg-slate-950/70 border border-slate-800 rounded-2xl p-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 transition-all resize-y"
            />
            <div className="flex justify-between items-center px-1 mt-1 text-xs text-slate-500">
              <span>{text.length} characters</span>
              <span>Pasted SMS, WhatsApp, Email, or UPI alert</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {!selectedFile ? (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center gap-3 ${
                dragOver 
                  ? "border-amber-500 bg-amber-500/5" 
                  : "border-slate-800 hover:border-slate-700 bg-slate-950/50 hover:bg-slate-950/80"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/webp"
                onChange={handleFileSelect}
                className="hidden"
              />
              <div className="w-12 h-12 rounded-2xl bg-slate-800/80 flex items-center justify-center text-amber-400">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-200">
                  {t.dropzoneTitle}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  {t.dropzoneSub}
                </p>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center shrink-0 overflow-hidden">
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="Upload Preview"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="truncate">
                  <p className="text-sm font-medium text-slate-200 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-slate-500">
                    {(selectedFile.size / 1024).toFixed(1)} KB • Gemini Vision OCR Ready
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                className="p-2 text-slate-400 hover:text-red-400 transition-colors rounded-lg hover:bg-slate-900"
                title="Remove image"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Optional Sender ID input */}
      <div className="mt-5">
        <label className="block text-xs font-semibold text-slate-400 mb-1.5">
          {t.senderLabel}
        </label>
        <input
          type="text"
          value={sender}
          onChange={(e) => setSender(e.target.value)}
          placeholder={t.senderPlaceholder}
          className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 transition-all"
        />
      </div>

      {/* Controls & Privacy */}
      <div className="mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
        
        {/* Privacy toggle */}
        <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-400 select-none">
          <input
            type="checkbox"
            checked={!saveHistory}
            onChange={(e) => setSaveHistory(!e.target.checked)}
            className="w-4 h-4 rounded bg-slate-950 border-slate-700 text-amber-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
          />
          <span className="flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-slate-500" />
            {t.privacyToggle}
          </span>
        </label>

        {/* Buttons */}
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {(text || selectedFile || sender) && (
            <button
              type="button"
              onClick={onClear}
              disabled={loading}
              className="px-4 py-2.5 rounded-xl border border-slate-800 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              {t.btnClear}
            </button>
          )}

          <button
            type="button"
            onClick={onOpenDemo}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-xs font-medium text-amber-300 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>{t.btnExamples}</span>
          </button>

          <button
            type="button"
            onClick={() => onAnalyze(activeTab)}
            disabled={!canSubmit || loading}
            className={`flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold transition-all shadow-lg ${
              canSubmit && !loading
                ? "bg-gradient-to-r from-red-600 via-amber-600 to-amber-500 hover:from-red-500 hover:to-amber-400 text-white shadow-red-600/25 hover:shadow-red-600/40 cursor-pointer hover:scale-[1.02]"
                : "bg-slate-800 text-slate-500 border border-slate-700/50 cursor-not-allowed"
            }`}
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>{t.btnAnalyzing}</span>
              </>
            ) : (
              <>
                <span>{t.btnAnalyze}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

      </div>

    </div>
  );
}
