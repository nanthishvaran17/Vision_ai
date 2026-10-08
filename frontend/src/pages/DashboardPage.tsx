import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { ConversationSummary } from '../lib/types';
import { CameraCaptureModal } from '../components/CameraCaptureModal';
import {
  ShieldCheck, Upload, Camera, FileText, SplitSquareVertical,
  Zap, MessageSquare, Plus, LogOut, Settings, ShieldAlert
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [showCamera, setShowCamera] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    async function loadConversations() {
      try {
        const data = await api.listConversations();
        setConversations(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadConversations();
  }, []);

  const handleStartNewChat = async (file?: File) => {
    try {
      setUploading(true);
      const conv = await api.createConversation("Visual Verification Session");
      if (file) {
        await api.uploadImage(conv.id, file);
      }
      navigate(`/chat/${conv.id}`);
    } catch (err: any) {
      alert(err.message || "Failed to initialize conversation");
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleStartNewChat(e.target.files[0]);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900/60 p-4 flex flex-col justify-between hidden md:flex">
        <div>
          <div className="flex items-center gap-3 px-2 py-3 border-b border-slate-800">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-white shadow-lg">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-bold text-sm tracking-wide">VISIONNEXT AI</h2>
              <p className="text-[10px] text-blue-400 font-medium">Verify. Don't Just See.</p>
            </div>
          </div>

          <button
            onClick={() => handleStartNewChat()}
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 font-medium text-sm text-white shadow-md hover:bg-blue-500 transition-all"
          >
            <Plus className="h-4 w-4" />
            New Verification Chat
          </button>

          <div className="mt-6">
            <h4 className="px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Recent Chats</h4>
            <div className="mt-2 space-y-1">
              {conversations.slice(0, 6).map((c) => (
                <button
                  key={c.id}
                  onClick={() => navigate(`/chat/${c.id}`)}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white transition-all text-left truncate"
                >
                  <MessageSquare className="h-3.5 w-3.5 text-blue-400 shrink-0" />
                  <span className="truncate">{c.title}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-3 space-y-1">
          <button
            onClick={() => navigate('/compare')}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <SplitSquareVertical className="h-4 w-4 text-slate-400" />
            Compare Mode
          </button>
          <button
            onClick={() => navigate('/settings')}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <Settings className="h-4 w-4 text-slate-400" />
            Settings
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 md:p-12 overflow-y-auto">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto text-center mt-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-semibold text-blue-400 backdrop-blur-md">
            <Zap className="h-3.5 w-3.5" /> CODIENYCH 2026 — Active Visual Verification Engine
          </div>
          <h1 className="mt-6 text-4xl md:text-5xl font-extrabold tracking-tight text-white">
            VISIONNEXT AI
          </h1>
          <p className="mt-3 text-lg md:text-xl font-medium text-blue-400">
            "Don't Just See. Verify."
          </p>
          <p className="mt-2 text-sm text-slate-400 max-w-xl mx-auto">
            Conversational computer vision system with zero fake labels, runtime pixel detection, spatial geometry, and hallucination rejection.
          </p>
        </div>

        {/* Upload Action Box */}
        <div className="max-w-2xl mx-auto mt-10">
          <div className="rounded-2xl border-2 border-dashed border-slate-700 bg-slate-900/80 p-8 text-center backdrop-blur-xl hover:border-blue-500 transition-all group">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600/20 text-blue-400 border border-blue-500/30 group-hover:scale-110 transition-transform">
              <Upload className="h-7 w-7" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-white">Upload Image for Visual Verification</h3>
            <p className="mt-1 text-xs text-slate-400">Drop JPEG, PNG, or WEBP image here or capture live</p>

            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <label className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-blue-500 cursor-pointer active:scale-95 transition-all">
                <Upload className="h-4 w-4" />
                Choose File
                <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
              </label>

              <button
                onClick={() => setShowCamera(true)}
                className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-5 py-2.5 text-sm font-semibold text-slate-200 hover:bg-slate-700 active:scale-95 transition-all"
              >
                <Camera className="h-4 w-4 text-blue-400" />
                Take Photo
              </button>
            </div>
          </div>
        </div>

        {/* Action Cards */}
        <div className="max-w-4xl mx-auto mt-12 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div
            onClick={() => handleStartNewChat()}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 hover:border-blue-500/50 cursor-pointer transition-all hover:-translate-y-1"
          >
            <div className="h-10 w-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h4 className="mt-3 font-semibold text-sm text-white">Analyze Image</h4>
            <p className="mt-1 text-xs text-slate-400">Detect objects & pixel boundaries with runtime confidence.</p>
          </div>

          <div
            onClick={() => handleStartNewChat()}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 hover:border-blue-500/50 cursor-pointer transition-all hover:-translate-y-1"
          >
            <div className="h-10 w-10 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <FileText className="h-5 w-5" />
            </div>
            <h4 className="mt-3 font-semibold text-sm text-white">Read Document</h4>
            <p className="mt-1 text-xs text-slate-400">Extract OCR text, dates, venues, and notice details.</p>
          </div>

          <div
            onClick={() => navigate('/compare')}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 hover:border-blue-500/50 cursor-pointer transition-all hover:-translate-y-1"
          >
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <SplitSquareVertical className="h-5 w-5" />
            </div>
            <h4 className="mt-3 font-semibold text-sm text-white">Compare Images</h4>
            <p className="mt-1 text-xs text-slate-400">Detect added, removed, moved objects between 2 photos.</p>
          </div>

          <div
            onClick={() => handleStartNewChat()}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 hover:border-blue-500/50 cursor-pointer transition-all hover:-translate-y-1"
          >
            <div className="h-10 w-10 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <h4 className="mt-3 font-semibold text-sm text-white">Challenge AI</h4>
            <p className="mt-1 text-xs text-slate-400">Test hallucination guard & active crop/zoom engine.</p>
          </div>
        </div>
      </main>

      {showCamera && (
        <CameraCaptureModal
          onCapture={(file) => handleStartNewChat(file)}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
};
