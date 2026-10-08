import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { ConversationSummary } from '../lib/types';
import { CameraCaptureModal } from '../components/CameraCaptureModal';
import { Sidebar } from '../components/Sidebar';
import { ThemeToggle } from '../components/ThemeToggle';
import {
  ShieldCheck, Upload, Camera, FileText, SplitSquareVertical,
  Zap, Plus, ShieldAlert, Sparkles, ArrowRight, Menu
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [showCamera, setShowCamera] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const loadConversations = async () => {
    try {
      const data = await api.listConversations();
      setConversations(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
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
    <div className="flex h-screen bg-[var(--bg-main)] text-[var(--text-main)] transition-colors duration-300 overflow-hidden relative">
      {/* Dynamic Background Glow Blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 dark:bg-blue-600/15 rounded-full filter blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-600/15 rounded-full filter blur-3xl pointer-events-none" />

      {/* Sidebar */}
      <Sidebar conversations={conversations} onStartNewChat={() => handleStartNewChat()} onRefreshConvs={loadConversations} />


      {/* Main Container */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto relative z-10">
        {/* Top Navbar / Mobile Header */}
        <header className="px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between sticky top-0 z-30 transition-colors duration-300">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 md:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            <div className="flex items-center gap-2 md:hidden">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white shadow-md">
                <ShieldCheck className="h-4 w-4" />
              </div>
              <span className="font-extrabold text-sm tracking-wide text-slate-900 dark:text-white">
                VISIONNEXT AI
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
            <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">
              System Online & Verification Engine Ready
            </span>
          </div>

          {/* Theme Toggle shown on mobile only since Sidebar contains primary Theme control on desktop */}
          <div className="flex items-center gap-3 md:hidden">
            <ThemeToggle showLabel={false} />
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 p-4 md:p-8 max-w-6xl mx-auto w-full flex flex-col justify-between">
          {/* Hero Section */}
          <div className="text-center mt-1 md:mt-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1 text-xs font-bold text-blue-600 dark:text-blue-400 backdrop-blur-md shadow-sm">
              <Zap className="h-3.5 w-3.5 text-blue-500 animate-bounce" />
              <span>CODIENYCH 2026 — Active Visual Verification Engine</span>
            </div>

            <h1 className="mt-3 text-3xl md:text-5xl font-black tracking-tight bg-gradient-to-r from-slate-900 via-blue-700 to-indigo-900 dark:from-white dark:via-blue-300 dark:to-indigo-300 bg-clip-text text-transparent">
              VISIONNEXT AI
            </h1>

            <p className="mt-1.5 text-lg md:text-xl font-bold text-blue-600 dark:text-blue-400 tracking-wide">
              "Don't Just See. Verify."
            </p>

            <p className="mt-2 text-xs md:text-sm text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed font-medium">
              Conversational computer vision system with zero fake labels, runtime pixel detection, spatial geometry, and hallucination rejection.
            </p>
          </div>

          {/* Animated Central Upload Card */}
          <div className="mt-5 max-w-xl mx-auto w-full">
            <div className="relative group rounded-3xl border-2 border-dashed border-blue-400/40 dark:border-blue-500/30 bg-white dark:bg-slate-900 p-6 md:p-8 text-center shadow-xl hover:border-blue-500 dark:hover:border-blue-400 transition-all duration-300 hover:shadow-2xl">
              
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Upload className="h-7 w-7 stroke-[2.2]" />
              </div>

              <h3 className="mt-3.5 text-lg font-extrabold text-slate-900 dark:text-white">
                Upload Image for Visual Verification
              </h3>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">
                Drop JPEG, PNG, or WEBP image here or capture live with your camera
              </p>

              {/* Action Buttons */}
              <div className="mt-5 flex flex-wrap justify-center items-center gap-3">
                <label className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg hover:from-blue-500 hover:to-indigo-500 cursor-pointer transition-all duration-200 hover:scale-105">
                  <Upload className="h-4 w-4 stroke-[2.5]" />
                  <span>Choose File</span>
                  <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
                </label>

                <button
                  onClick={() => setShowCamera(true)}
                  className="flex items-center gap-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 px-5 py-2.5 text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 shadow-sm transition-all duration-200 hover:scale-105"
                >
                  <Camera className="h-4 w-4 text-blue-600 dark:text-blue-400 stroke-[2.5]" />
                  <span>Take Photo</span>
                </button>
              </div>

              {uploading && (
                <div className="mt-4 flex items-center justify-center gap-2 text-xs font-semibold text-blue-600 dark:text-blue-400 animate-pulse">
                  <Sparkles className="h-4 w-4 animate-spin" /> Uploading image and starting verification session...
                </div>
              )}
            </div>
          </div>

          {/* Feature Cards Grid */}
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pb-4">
            {/* Card 1: Analyze Image */}
            <div
              onClick={() => handleStartNewChat()}
              className="group relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 hover:border-blue-500/60 dark:hover:border-blue-400/60 cursor-pointer transition-all duration-300 hover:-translate-y-1 shadow-sm hover:shadow-lg"
            >
              <div className="h-9 w-9 rounded-xl bg-blue-500/15 text-blue-600 dark:text-blue-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h4 className="mt-3 font-bold text-sm text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex items-center justify-between">
                Analyze Image
                <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity text-blue-600 dark:text-blue-400" />
              </h4>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
                Detect objects & pixel boundaries with runtime confidence.
              </p>
            </div>

            {/* Card 2: Read Document */}
            <div
              onClick={() => handleStartNewChat()}
              className="group relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 hover:border-purple-500/60 dark:hover:border-purple-400/60 cursor-pointer transition-all duration-300 hover:-translate-y-1 shadow-sm hover:shadow-lg"
            >
              <div className="h-9 w-9 rounded-xl bg-purple-500/15 text-purple-600 dark:text-purple-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FileText className="h-5 w-5" />
              </div>
              <h4 className="mt-3 font-bold text-sm text-slate-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors flex items-center justify-between">
                Read Document
                <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity text-purple-600 dark:text-purple-400" />
              </h4>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
                Extract OCR text, dates, venues, and document details.
              </p>
            </div>

            {/* Card 3: Compare Images */}
            <div
              onClick={() => navigate('/compare')}
              className="group relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 hover:border-emerald-500/60 dark:hover:border-emerald-400/60 cursor-pointer transition-all duration-300 hover:-translate-y-1 shadow-sm hover:shadow-lg"
            >
              <div className="h-9 w-9 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <SplitSquareVertical className="h-5 w-5" />
              </div>
              <h4 className="mt-3 font-bold text-sm text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors flex items-center justify-between">
                Compare Mode
                <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity text-emerald-600 dark:text-emerald-400" />
              </h4>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
                Detect added, removed, or moved objects between 2 photos.
              </p>
            </div>

            {/* Card 4: Challenge AI */}
            <div
              onClick={() => handleStartNewChat()}
              className="group relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 hover:border-amber-500/60 dark:hover:border-amber-400/60 cursor-pointer transition-all duration-300 hover:-translate-y-1 shadow-sm hover:shadow-lg"
            >
              <div className="h-9 w-9 rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <h4 className="mt-3 font-bold text-sm text-slate-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors flex items-center justify-between">
                Challenge AI
                <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity text-amber-600 dark:text-amber-400" />
              </h4>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
                Test hallucination guard & active crop/zoom verification.
              </p>
            </div>
          </div>
        </main>
      </div>

      {showCamera && (
        <CameraCaptureModal
          onCapture={(file) => handleStartNewChat(file)}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
};
