import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { ImageComparisonResponse, ConversationSummary } from '../lib/types';
import { Sidebar } from '../components/Sidebar';
import { ThemeToggle } from '../components/ThemeToggle';
import { SplitSquareVertical, Upload, ArrowLeft, Plus, Minus, Move, CheckCircle2, Sparkles } from 'lucide-react';

export const ComparePage: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [previewA, setPreviewA] = useState<string | null>(null);
  const [previewB, setPreviewB] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState<ImageComparisonResponse | null>(null);

  useEffect(() => {
    async function loadConvs() {
      try {
        const data = await api.listConversations();
        setConversations(data);
      } catch (e) {}
    }
    loadConvs();
  }, []);

  const handleSelectA = (file: File) => {
    setFileA(file);
    setPreviewA(URL.createObjectURL(file));
  };

  const handleSelectB = (file: File) => {
    setFileB(file);
    setPreviewB(URL.createObjectURL(file));
  };

  const handleRunComparison = async () => {
    if (!fileA || !fileB) return;
    setLoading(true);
    try {
      let convId = "";
      try {
        const conv = await api.createConversation("Comparison Session");
        convId = conv.id;
      } catch (e) {}

      const imgA = await api.uploadImage(convId, fileA);
      const imgB = await api.uploadImage(convId, fileB);

      const comp = await api.compareImages(imgA.id, imgB.id);
      setComparison(comp);
    } catch (err: any) {
      alert(err.message || "Failed to compare images");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[var(--bg-main)] text-[var(--text-main)] transition-colors duration-300 overflow-hidden">
      <Sidebar conversations={conversations} />

      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <header className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md flex items-center justify-between sticky top-0 z-30 transition-colors duration-300">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Dashboard
          </button>
          <div className="md:hidden">
            <ThemeToggle showLabel={false} />
          </div>
        </header>

        <main className="flex-1 p-6 md:p-12 max-w-5xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 animate-pulse-glow">
              <SplitSquareVertical className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">
                Visual Image Comparison Mode
              </h1>
              <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400">
                Detect added, removed, moved objects and text changes between BEFORE & AFTER
              </p>
            </div>
          </div>

          {/* Upload Slots A & B */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Image A (Before) */}
            <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6 text-center shadow-lg backdrop-blur-xl">
              <h3 className="text-sm font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">Image A (Before)</h3>
              {previewA ? (
                <div className="mt-4 overflow-hidden rounded-2xl bg-black shadow-md">
                  <img src={previewA} alt="Before" className="max-h-64 mx-auto object-contain" />
                </div>
              ) : (
                <label className="mt-4 flex flex-col items-center justify-center h-52 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl cursor-pointer hover:border-blue-500 transition-colors">
                  <Upload className="h-8 w-8 text-slate-400" />
                  <span className="mt-2 text-xs font-semibold text-slate-600 dark:text-slate-400">Upload Before Image</span>
                  <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handleSelectA(e.target.files[0])} className="hidden" />
                </label>
              )}
            </div>

            {/* Image B (After) */}
            <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6 text-center shadow-lg backdrop-blur-xl">
              <h3 className="text-sm font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Image B (After)</h3>
              {previewB ? (
                <div className="mt-4 overflow-hidden rounded-2xl bg-black shadow-md">
                  <img src={previewB} alt="After" className="max-h-64 mx-auto object-contain" />
                </div>
              ) : (
                <label className="mt-4 flex flex-col items-center justify-center h-52 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl cursor-pointer hover:border-emerald-500 transition-colors">
                  <Upload className="h-8 w-8 text-slate-400" />
                  <span className="mt-2 text-xs font-semibold text-slate-600 dark:text-slate-400">Upload After Image</span>
                  <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handleSelectB(e.target.files[0])} className="hidden" />
                </label>
              )}
            </div>
          </div>

          {fileA && fileB && !comparison && (
            <div className="mt-8 text-center">
              <button
                onClick={handleRunComparison}
                disabled={loading}
                className="rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 px-8 py-3.5 font-bold text-white shadow-xl hover:from-emerald-500 hover:to-teal-500 btn-animated animate-pulse-glow disabled:opacity-50 transition-all"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 animate-spin" /> Analyzing Differences...
                  </span>
                ) : (
                  "Compare Images Now"
                )}
              </button>
            </div>
          )}

          {/* Comparison Results Dashboard */}
          {comparison && (
            <div className="mt-10 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900 p-6 md:p-8 shadow-2xl backdrop-blur-xl">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                Comparison Audit Summary
              </h3>
              <p className="mt-3 text-sm text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50 leading-relaxed">
                {comparison.summary}
              </p>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                {/* Added */}
                <div className="rounded-2xl border border-emerald-500/30 bg-emerald-50 dark:bg-emerald-950/20 p-4">
                  <span className="font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                    <Plus className="h-4 w-4" /> Added Objects ({comparison.added_objects.length})
                  </span>
                  <ul className="mt-2 space-y-1 text-slate-700 dark:text-slate-300 font-medium">
                    {comparison.added_objects.map((o, idx) => (
                      <li key={idx}>+ {o.label} ({Math.round(o.confidence * 100)}%)</li>
                    ))}
                    {comparison.added_objects.length === 0 && <li className="text-slate-400">None</li>}
                  </ul>
                </div>

                {/* Removed */}
                <div className="rounded-2xl border border-red-500/30 bg-red-50 dark:bg-red-950/20 p-4">
                  <span className="font-bold text-red-700 dark:text-red-400 flex items-center gap-1.5">
                    <Minus className="h-4 w-4" /> Removed Objects ({comparison.removed_objects.length})
                  </span>
                  <ul className="mt-2 space-y-1 text-slate-700 dark:text-slate-300 font-medium">
                    {comparison.removed_objects.map((o, idx) => (
                      <li key={idx}>- {o.label}</li>
                    ))}
                    {comparison.removed_objects.length === 0 && <li className="text-slate-400">None</li>}
                  </ul>
                </div>

                {/* Moved */}
                <div className="rounded-2xl border border-blue-500/30 bg-blue-50 dark:bg-blue-950/20 p-4">
                  <span className="font-bold text-blue-700 dark:text-blue-400 flex items-center gap-1.5">
                    <Move className="h-4 w-4" /> Moved Objects ({comparison.moved_objects.length})
                  </span>
                  <ul className="mt-2 space-y-1 text-slate-700 dark:text-slate-300 font-medium">
                    {comparison.moved_objects.map((m, idx) => (
                      <li key={idx}>~ {m.label} (shifted {m.shift_distance})</li>
                    ))}
                    {comparison.moved_objects.length === 0 && <li className="text-slate-400">None</li>}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
