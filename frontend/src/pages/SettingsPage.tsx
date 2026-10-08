import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings, Cpu, Shield, Save, LogOut } from 'lucide-react';
import { clearTokens } from '../lib/api';

export const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [provider, setProvider] = useState('openai');
  const [ocrProvider, setOcrProvider] = useState('easyocr');

  const handleLogout = () => {
    clearTokens();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6 md:p-12 text-slate-100">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white mb-6"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </button>

        <div className="flex items-center gap-3 mb-8">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Settings className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Verification Engine Settings</h1>
            <p className="text-xs text-slate-400">Configure AI models, OCR engines, and security thresholds</p>
          </div>
        </div>

        <div className="space-y-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">Multimodal LLM Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-800 py-2.5 px-3 text-sm text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="openai">OpenAI Multimodal (GPT-4o / GPT-4o-mini)</option>
              <option value="ollama">Ollama Local (llava / qwen2.5-vl)</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">OCR Text Engine</label>
            <select
              value={ocrProvider}
              onChange={(e) => setOcrProvider(e.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-800 py-2.5 px-3 text-sm text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="easyocr">EasyOCR (Deep Learning Text Reader)</option>
              <option value="tesseract">PyTesseract (Tesseract Engine)</option>
              <option value="opencv">OpenCV MSER Region Detection</option>
            </select>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-between items-center">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-xl border border-red-500/40 bg-red-950/20 px-4 py-2.5 text-xs font-semibold text-red-300 hover:bg-red-900/40"
            >
              <LogOut className="h-4 w-4" /> Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
