import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { ImageComparisonResponse } from '../lib/types';
import { SplitSquareVertical, Upload, ArrowLeft, Plus, Minus, Move, CheckCircle2 } from 'lucide-react';

export const ComparePage: React.FC = () => {
  const navigate = useNavigate();
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [previewA, setPreviewA] = useState<string | null>(null);
  const [previewB, setPreviewB] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState<ImageComparisonResponse | null>(null);

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
    <div className="min-h-screen bg-slate-950 p-6 md:p-12 text-slate-100">
      <div className="max-w-5xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white mb-6"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </button>

        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <SplitSquareVertical className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Visual Image Comparison Mode</h1>
            <p className="text-xs text-slate-400">Detect added, removed, moved objects and text changes between BEFORE & AFTER</p>
          </div>
        </div>

        {/* Upload Slots A & B */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Image A (Before) */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 text-center">
            <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider">Image A (Before)</h3>
            {previewA ? (
              <div className="mt-4 overflow-hidden rounded-xl bg-black">
                <img src={previewA} alt="Before" className="max-h-64 mx-auto object-contain" />
              </div>
            ) : (
              <label className="mt-4 flex flex-col items-center justify-center h-52 border-2 border-dashed border-slate-700 rounded-xl cursor-pointer hover:border-blue-500">
                <Upload className="h-8 w-8 text-slate-500" />
                <span className="mt-2 text-xs text-slate-400">Upload Before Image</span>
                <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handleSelectA(e.target.files[0])} className="hidden" />
              </label>
            )}
          </div>

          {/* Image B (After) */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 text-center">
            <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider">Image B (After)</h3>
            {previewB ? (
              <div className="mt-4 overflow-hidden rounded-xl bg-black">
                <img src={previewB} alt="After" className="max-h-64 mx-auto object-contain" />
              </div>
            ) : (
              <label className="mt-4 flex flex-col items-center justify-center h-52 border-2 border-dashed border-slate-700 rounded-xl cursor-pointer hover:border-emerald-500">
                <Upload className="h-8 w-8 text-slate-500" />
                <span className="mt-2 text-xs text-slate-400">Upload After Image</span>
                <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handleSelectB(e.target.files[0])} className="hidden" />
              </label>
            )}
          </div>
        </div>

        {fileA && fileB && !comparison && (
          <div className="mt-6 text-center">
            <button
              onClick={handleRunComparison}
              disabled={loading}
              className="rounded-xl bg-emerald-600 px-8 py-3 font-semibold text-white shadow-xl hover:bg-emerald-500 disabled:opacity-50 transition-all"
            >
              {loading ? "Analyzing Differences..." : "Compare Images Now"}
            </button>
          </div>
        )}

        {/* Comparison Results Dashboard */}
        {comparison && (
          <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              Comparison Audit Summary
            </h3>
            <p className="mt-2 text-sm text-slate-300 bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
              {comparison.summary}
            </p>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              {/* Added */}
              <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
                <span className="font-bold text-emerald-400 flex items-center gap-1.5">
                  <Plus className="h-4 w-4" /> Added Objects ({comparison.added_objects.length})
                </span>
                <ul className="mt-2 space-y-1 text-slate-300">
                  {comparison.added_objects.map((o, idx) => (
                    <li key={idx}>+ {o.label} ({Math.round(o.confidence * 100)}%)</li>
                  ))}
                  {comparison.added_objects.length === 0 && <li className="text-slate-500">None</li>}
                </ul>
              </div>

              {/* Removed */}
              <div className="rounded-xl border border-red-500/30 bg-red-950/20 p-4">
                <span className="font-bold text-red-400 flex items-center gap-1.5">
                  <Minus className="h-4 w-4" /> Removed Objects ({comparison.removed_objects.length})
                </span>
                <ul className="mt-2 space-y-1 text-slate-300">
                  {comparison.removed_objects.map((o, idx) => (
                    <li key={idx}>- {o.label}</li>
                  ))}
                  {comparison.removed_objects.length === 0 && <li className="text-slate-500">None</li>}
                </ul>
              </div>

              {/* Moved */}
              <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 p-4">
                <span className="font-bold text-blue-400 flex items-center gap-1.5">
                  <Move className="h-4 w-4" /> Moved Objects ({comparison.moved_objects.length})
                </span>
                <ul className="mt-2 space-y-1 text-slate-300">
                  {comparison.moved_objects.map((m, idx) => (
                    <li key={idx}>~ {m.label} (shifted {m.shift_distance})</li>
                  ))}
                  {comparison.moved_objects.length === 0 && <li className="text-slate-500">None</li>}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
