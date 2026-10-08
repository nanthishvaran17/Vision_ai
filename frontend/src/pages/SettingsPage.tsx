import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings, Cpu, Shield, Save, LogOut } from 'lucide-react';
import { clearTokens, api } from '../lib/api';
import { ConversationSummary } from '../lib/types';
import { Sidebar } from '../components/Sidebar';
import { ThemeToggle } from '../components/ThemeToggle';

export const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [provider, setProvider] = useState('openai');
  const [ocrProvider, setOcrProvider] = useState('easyocr');

  useEffect(() => {
    async function loadConvs() {
      try {
        const data = await api.listConversations();
        setConversations(data);
      } catch (e) {}
    }
    loadConvs();
  }, []);

  const handleLogout = () => {
    clearTokens();
    navigate('/login');
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

        <main className="flex-1 p-6 md:p-12 max-w-3xl mx-auto w-full">
          <div className="flex items-center gap-3 mb-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600/20 text-blue-600 dark:text-blue-400 border border-blue-500/30 animate-pulse-glow">
              <Settings className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Verification Engine Settings</h1>
              <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400">Configure AI models, OCR engines, visual grounding, and security thresholds</p>
            </div>
          </div>

          <div className="space-y-6 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900 p-6 md:p-8 shadow-xl backdrop-blur-xl">
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                <Cpu className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                Multimodal LLM Provider
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="mt-2.5 w-full rounded-2xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 py-3 px-4 text-sm font-medium text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none transition-all shadow-sm"
              >
                <option value="openai">OpenAI Multimodal (GPT-4o / GPT-4o-mini)</option>
                <option value="ollama">Ollama Local (llava / qwen2.5-vl)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                <Shield className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                OCR Text Engine
              </label>
              <select
                value={ocrProvider}
                onChange={(e) => setOcrProvider(e.target.value)}
                className="mt-2.5 w-full rounded-2xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 py-3 px-4 text-sm font-medium text-slate-900 dark:text-white focus:border-blue-500 focus:outline-none transition-all shadow-sm"
              >
                <option value="easyocr">EasyOCR (Deep Learning Text Reader)</option>
                <option value="tesseract">PyTesseract (Tesseract Engine)</option>
                <option value="opencv">OpenCV MSER Region Detection</option>
              </select>
            </div>

            {/* Appearance Theme Selector */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Interface Color Scheme
              </label>
              <div className="mt-2.5 flex items-center justify-between p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">Dark / Light Mode</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Toggle active visual theme across all pages</p>
                </div>
                <ThemeToggle showLabel={true} />
              </div>
            </div>

            <div className="pt-6 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center">
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-2xl border border-red-500/40 bg-red-50 dark:bg-red-950/20 px-5 py-3 text-xs font-bold text-red-600 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/40 btn-animated transition-all"
              >
                <LogOut className="h-4 w-4" /> Sign Out
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
