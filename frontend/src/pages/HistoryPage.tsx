import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { ConversationSummary } from '../lib/types';
import { MessageSquare, ArrowLeft, Trash2, Calendar } from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.listConversations();
        setConversations(data);
      } catch (e) {}
    }
    load();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Delete this conversation history?")) {
      await api.deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6 md:p-12 text-slate-100">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white mb-6"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </button>

        <h1 className="text-2xl font-bold text-white mb-6">Conversation Verification History</h1>

        <div className="space-y-3">
          {conversations.map((c) => (
            <div
              key={c.id}
              onClick={() => navigate(`/chat/${c.id}`)}
              className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 p-4 hover:border-blue-500/50 cursor-pointer transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600/20 text-blue-400">
                  <MessageSquare className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-sm text-white">{c.title}</h4>
                  <p className="text-xs text-slate-400 mt-0.5 truncate max-w-md">{c.last_message || "No messages"}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <span className="text-xs font-mono text-slate-500 flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  {new Date(c.updated_at).toLocaleDateString()}
                </span>
                <button
                  onClick={(e) => handleDelete(c.id, e)}
                  className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-800 hover:text-red-400"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
