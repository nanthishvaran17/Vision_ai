import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, getAuthToken } from '../lib/api';
import { Conversation, Message, DetectedObject, WhyThisAnswerPayload } from '../lib/types';
import { VisualGroundingOverlay } from '../components/VisualGroundingOverlay';
import { ObjectDetailPanel } from '../components/ObjectDetailPanel';
import { WhyThisAnswerModal } from '../components/WhyThisAnswerModal';
import { CameraCaptureModal } from '../components/CameraCaptureModal';
import { LiveVerificationProgress } from '../components/LiveVerificationProgress';
import { VoiceRecognizer } from '../features/voice/voice';
import {
  ShieldCheck, Send, Mic, Camera, Upload, Plus, ShieldAlert,
  HelpCircle, ChevronRight, CornerDownLeft, Sparkles, MessageSquare, Menu
} from 'lucide-react';

export const ChatPage: React.FC = () => {
  const { id: conversationId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputContent, setInputContent] = useState('');
  const [activeImageId, setActiveImageId] = useState<string | undefined>(undefined);
  const [activeImageUrl, setActiveImageUrl] = useState<string | null>(null);
  const [objects, setObjects] = useState<DetectedObject[]>([]);
  const [selectedObject, setSelectedObject] = useState<DetectedObject | null>(null);
  const [whyModalPayload, setWhyModalPayload] = useState<WhyThisAnswerPayload | null>(null);

  const [isChallengeMode, setIsChallengeMode] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [wsSteps, setWsSteps] = useState<any[]>([]);
  const [wsStatusText, setWsStatusText] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const voiceRecognizerRef = useRef<VoiceRecognizer | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!conversationId) return;

    async function loadConv() {
      try {
        const data = await api.getConversation(conversationId!);
        setConversation(data);
        setMessages(data.messages || []);
        
        // Find latest uploaded image in message metadata
        const imgMsg = [...(data.messages || [])].reverse().find(m => m.metadata_json);
        if (imgMsg && imgMsg.metadata_json) {
          try {
            const meta = JSON.parse(imgMsg.metadata_json);
            if (meta.annotations) {
              setObjects(meta.annotations);
            }
          } catch (e) {}
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadConv();

    // WebSocket connection setup
    const token = getAuthToken();
    if (!token) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/conversations/${conversationId}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event === 'verification_step_completed') {
          setWsSteps(prev => [...prev, { name: payload.data.description, status: 'completed' }]);
        } else if (payload.event === 'analysis_started') {
          setWsStatusText(payload.data.message);
        }
      } catch (e) {}
    };

    return () => {
      ws.close();
    };
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, wsSteps]);

  // Voice setup
  const toggleVoice = () => {
    if (!voiceRecognizerRef.current) {
      voiceRecognizerRef.current = new VoiceRecognizer(
        (transcript) => setInputContent(transcript),
        (err) => console.error(err)
      );
    }
    if (isListening) {
      voiceRecognizerRef.current.stop();
      setIsListening(false);
    } else {
      voiceRecognizerRef.current.start();
      setIsListening(true);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputContent;
    if (!text.trim() || !conversationId) return;

    setInputContent('');
    setIsProcessing(true);
    setWsSteps([]);

    // Optimistic User Message
    const userMsgTemp: Message = {
      id: `temp_${Date.now()}`,
      conversation_id: conversationId,
      role: 'user',
      content: text,
      message_type: 'USER_TEXT',
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsgTemp]);

    try {
      const aiResp = await api.sendMessage(conversationId, text, activeImageId, isChallengeMode);
      setMessages(prev => [...prev.filter(m => !m.id.startsWith('temp_')), aiResp]);
      if (aiResp.why_this_answer?.annotations) {
        setObjects(aiResp.why_this_answer.annotations);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to process message');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleImageSelected = async (file: File) => {
    if (!conversationId) return;
    try {
      setIsProcessing(true);
      const imgResp = await api.uploadImage(conversationId, file);
      setActiveImageId(imgResp.id);
      setActiveImageUrl(`/uploads/${imgResp.file_path}`);
      
      // Auto trigger initial verification analysis
      handleSend("What objects can you identify in this image?");
    } catch (err: any) {
      alert(err.message || "Failed to upload image");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Central Chat Container */}
      <div className="flex flex-1 flex-col h-full overflow-hidden">
        {/* Header Bar */}
        <header className="flex items-center justify-between border-b border-slate-800 bg-slate-900/80 px-6 py-3.5 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/dashboard')} className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800">
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-6 w-6 text-blue-400" />
              <h2 className="font-bold text-base text-white">{conversation?.title || "Verification Chat"}</h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsChallengeMode(!isChallengeMode)}
              className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all ${
                isChallengeMode
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-lg'
                  : 'bg-slate-800/80 text-slate-400 border-slate-700 hover:text-white'
              }`}
            >
              <ShieldAlert className="h-4 w-4" />
              Challenge AI Mode
            </button>
          </div>
        </header>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            const whyData = msg.why_this_answer;

            return (
              <div key={msg.id} className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
                {!isUser && (
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400">
                    <Sparkles className="h-5 w-5" />
                  </div>
                )}

                <div className={`max-w-2xl space-y-3 ${isUser ? 'items-end' : 'items-start'}`}>
                  {/* Text Bubble */}
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      isUser
                        ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                        : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-none shadow-xl'
                    }`}
                  >
                    {msg.content}
                  </div>

                  {/* Why This Answer Badge */}
                  {!isUser && whyData && (
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`rounded-md border px-2 py-0.5 text-[11px] font-bold ${
                          whyData.confidence === 'HIGH'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                        }`}
                      >
                        {whyData.confidence} EVIDENCE
                      </span>

                      <button
                        onClick={() => setWhyModalPayload(whyData)}
                        className="flex items-center gap-1 rounded-md border border-slate-700 bg-slate-800/80 px-2.5 py-0.5 text-xs text-blue-300 hover:bg-slate-700"
                      >
                        <HelpCircle className="h-3.5 w-3.5" />
                        Show me why
                      </button>
                    </div>
                  )}

                  {/* Suggested Followups Chips */}
                  {!isUser && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {["Read document text", "What color is the primary object?", "What is next to it?"].map((chip, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(chip)}
                          className="rounded-full border border-slate-800 bg-slate-900/90 px-3 py-1 text-xs text-slate-400 hover:border-blue-500/50 hover:text-blue-300 transition-all"
                        >
                          {chip}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Live Progress Bar during active processing */}
          {isProcessing && (
            <LiveVerificationProgress
              steps={wsSteps.length > 0 ? wsSteps : [{ name: 'Verifying image pixels...', status: 'active' }]}
              currentStatusText={wsStatusText}
            />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Composer */}
        <div className="border-t border-slate-800 bg-slate-900/90 p-4 backdrop-blur-xl">
          <div className="max-w-4xl mx-auto relative flex items-center gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="rounded-xl border border-slate-700 bg-slate-800 p-2.5 text-slate-400 hover:text-white hover:bg-slate-700"
            >
              <Plus className="h-5 w-5" />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              onChange={(e) => e.target.files?.[0] && handleImageSelected(e.target.files[0])}
              className="hidden"
            />

            <button
              onClick={() => setShowCamera(true)}
              className="rounded-xl border border-slate-700 bg-slate-800 p-2.5 text-slate-400 hover:text-white hover:bg-slate-700"
            >
              <Camera className="h-5 w-5 text-blue-400" />
            </button>

            <input
              type="text"
              value={inputContent}
              onChange={(e) => setInputContent(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder={activeImageUrl ? "Ask any visual, spatial, or OCR verification question..." : "Upload image or ask question..."}
              className="flex-1 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />

            <button
              onClick={toggleVoice}
              className={`rounded-xl border p-2.5 transition-all ${
                isListening ? 'bg-red-600 text-white border-red-500 animate-pulse' : 'border-slate-700 bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <Mic className="h-5 w-5" />
            </button>

            <button
              onClick={() => handleSend()}
              disabled={isProcessing || !inputContent.trim()}
              className="rounded-xl bg-blue-600 p-3 text-white shadow-lg hover:bg-blue-500 disabled:opacity-50 transition-all"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Right Side Grounding Evidence Panel */}
      {activeImageUrl && (
        <aside className="w-96 border-l border-slate-800 bg-slate-900/60 p-5 hidden lg:flex flex-col overflow-y-auto">
          <h3 className="font-bold text-sm text-white border-b border-slate-800 pb-3 flex items-center justify-between">
            <span>Visual Evidence Grounding</span>
            <span className="text-xs font-mono text-blue-400">{objects.length} Detections</span>
          </h3>

          <div className="mt-4">
            <VisualGroundingOverlay
              imageSrc={activeImageUrl}
              objects={objects}
              onSelectObject={(obj) => setSelectedObject(obj)}
            />
          </div>

          <div className="mt-6 flex-1">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Detected Objects</h4>
            <div className="space-y-2">
              {objects.map((obj) => (
                <div
                  key={obj.id}
                  onClick={() => setSelectedObject(obj)}
                  className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-xs hover:border-blue-500/50 cursor-pointer transition-all"
                >
                  <span className="font-medium text-slate-200 capitalize">{obj.label}</span>
                  <span className="font-mono text-emerald-400">{Math.round(obj.confidence * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        </aside>
      )}

      {/* Object Detail Slide-out */}
      <ObjectDetailPanel
        object={selectedObject}
        onClose={() => setSelectedObject(null)}
        onAskAboutObject={(label) => handleSend(`Tell me details about the ${label}`)}
      />

      {/* Why This Answer Audit Modal */}
      <WhyThisAnswerModal
        payload={whyModalPayload}
        onClose={() => setWhyModalPayload(null)}
      />

      {/* Camera Capture Dialog */}
      {showCamera && (
        <CameraCaptureModal
          onCapture={(file) => handleImageSelected(file)}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
};
