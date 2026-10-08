import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ConversationSummary } from '../lib/types';
import { ThemeToggle } from './ThemeToggle';
import {
  ShieldCheck, Plus, MessageSquare, SplitSquareVertical,
  Settings, LogOut, Home, History, Trash2
} from 'lucide-react';
import { clearTokens, api } from '../lib/api';

interface SidebarProps {
  conversations?: ConversationSummary[];
  onStartNewChat?: () => void;
  onRefreshConvs?: () => void;
  activeConvId?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations = [],
  onStartNewChat,
  onRefreshConvs,
  activeConvId
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    clearTokens();
    navigate('/login');
  };

  const handleNewChat = () => {
    if (onStartNewChat) {
      onStartNewChat();
    } else {
      navigate('/dashboard');
    }
  };

  const handleDeleteConv = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      if (activeConvId === id) {
        navigate('/dashboard');
      }
      if (onRefreshConvs) {
        onRefreshConvs();
      } else {
        window.location.reload();
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  return (

    <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 flex flex-col justify-between hidden md:flex transition-colors duration-300 shrink-0">
      <div>
        {/* Brand Header */}
        <div
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-3 px-2 py-3 border-b border-slate-200 dark:border-slate-800 cursor-pointer group"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-lg group-hover:scale-105 transition-transform animate-pulse-glow">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h2 className="font-bold text-sm tracking-wide text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              VISIONNEXT AI
            </h2>
            <p className="text-[10px] text-blue-600 dark:text-blue-400 font-semibold tracking-wider">
              Verify. Don't Just See.
            </p>
          </div>
        </div>

        {/* Animated New Chat Button */}
        <button
          onClick={handleNewChat}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 py-3 font-semibold text-sm text-white shadow-lg hover:from-blue-500 hover:to-indigo-500 btn-animated animate-pulse-glow"
        >
          <Plus className="h-4 w-4 stroke-[3]" />
          New Verification Chat
        </button>

        {/* Quick Nav Links */}
        <div className="mt-6 space-y-1">
          <button
            onClick={() => navigate('/dashboard')}
            className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold transition-all ${
              location.pathname === '/dashboard'
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800/50'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Home className="h-4 w-4" />
            Dashboard Home
          </button>

          <button
            onClick={() => navigate('/compare')}
            className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold transition-all ${
              location.pathname === '/compare'
                ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <SplitSquareVertical className="h-4 w-4 text-emerald-500" />
            Compare Mode
          </button>
        </div>

        {/* Recent Verification Chats */}
        {conversations.length > 0 && (
          <div className="mt-6">
            <h4 className="px-2 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center justify-between">
              <span>Recent Verifications</span>
              <span className="text-[10px] font-mono text-slate-400">{conversations.length}</span>
            </h4>
            <div className="mt-2 space-y-1 max-h-56 overflow-y-auto pr-1">
              {conversations.slice(0, 10).map((c) => {
                const isActive = activeConvId === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => navigate(`/chat/${c.id}`)}
                    className={`group flex items-center justify-between rounded-lg px-2.5 py-2 text-xs font-medium transition-all cursor-pointer ${
                      isActive
                        ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 font-semibold shadow-sm'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate pr-1">
                      <MessageSquare className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                      <span className="truncate max-w-[130px]">{c.title || 'Verification Session'}</span>
                    </div>
                    
                    <button
                      onClick={(e) => handleDeleteConv(e, c.id)}
                      title="Delete session"
                      className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 rounded transition-opacity"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

      </div>

      {/* Footer / Controls */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-4 space-y-2">
        {/* Theme Switcher Bar */}
        <div className="flex items-center justify-between px-2 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/50">
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Theme</span>
          <ThemeToggle showLabel={true} />
        </div>

        <button
          onClick={() => navigate('/settings')}
          className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold transition-all ${
            location.pathname === '/settings'
              ? 'bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-white'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Settings className="h-4 w-4" />
          Engine Settings
        </button>

        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-all"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};
