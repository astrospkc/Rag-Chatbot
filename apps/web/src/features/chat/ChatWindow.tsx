import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Send,
  Bot,
  User,
  UserCheck,
  AlertTriangle,
  BookOpen,
  Sparkles,
  ShieldAlert
} from 'lucide-react';

export const ChatWindow: React.FC = () => {
  const { messages, sendMessage, isBotThinking } = useApp();
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isBotThinking]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    sendMessage(inputText);
    setInputText('');
  };

  const handlePresetQuery = (queryText: string) => {
    sendMessage(queryText);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] max-w-5xl mx-auto px-4 py-4">
      {/* Header Info Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-t-2xl p-4 flex items-center justify-between shadow-md">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow">
              <Bot className="w-5 h-5" />
            </div>
            <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full"></span>
          </div>
          <div>
            <h2 className="text-white font-semibold text-sm flex items-center gap-2">
              Company AI Assistant
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/30">
                RAG Active
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Answers generated using company docs • Escalates on refusal
            </p>
          </div>
        </div>

        {/* Dynamic Status / Preset triggers */}
        <div className="hidden sm:flex items-center space-x-2 text-xs">
          <button
            onClick={() => handlePresetQuery('What is your standard refund policy timing?')}
            className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
          >
            Policy Query
          </button>
          <button
            onClick={() => handlePresetQuery('Can you grant custom escrow access for legal dispute?')}
            className="bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 px-2.5 py-1.5 rounded-lg border border-amber-500/30 transition flex items-center gap-1"
          >
            <ShieldAlert className="w-3 h-3" />
            Trigger Refusal/Escalation
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 bg-slate-950/70 border-x border-slate-800/80 p-4 sm:p-6 overflow-y-auto space-y-6">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const isAgent = msg.sender === 'agent';

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-2`}
            >
              <div className="flex items-start space-x-2 max-w-3xl">
                {!isUser && (
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center text-white shrink-0 mt-1 ${
                      isAgent
                        ? 'bg-amber-600'
                        : msg.isRefused
                        ? 'bg-rose-600'
                        : 'bg-indigo-600'
                    }`}
                  >
                    {isAgent ? (
                      <UserCheck className="w-4 h-4" />
                    ) : (
                      <Bot className="w-4 h-4" />
                    )}
                  </div>
                )}

                <div
                  className={`rounded-2xl px-4 py-3 text-sm shadow-md leading-relaxed ${
                    isUser
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : isAgent
                      ? 'bg-slate-800 text-slate-100 border border-amber-500/40 rounded-bl-none'
                      : msg.isRefused
                      ? 'bg-slate-900 text-slate-200 border border-rose-500/40 rounded-bl-none'
                      : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-none'
                  }`}
                >
                  {/* Agent Header Tag */}
                  {isAgent && (
                    <div className="flex items-center space-x-1.5 text-xs text-amber-400 font-semibold mb-2 pb-1 border-b border-amber-500/20">
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>Employee Support Agent ({msg.agentName})</span>
                    </div>
                  )}

                  {/* Refusal Banner */}
                  {msg.isRefused && (
                    <div className="flex items-center space-x-2 text-xs text-rose-400 bg-rose-500/10 px-3 py-1.5 rounded-md border border-rose-500/20 mb-2.5">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      <span className="font-semibold">
                        Query Refused by AI Guardrails • Human Escalation Initialized
                      </span>
                    </div>
                  )}

                  <p className="whitespace-pre-wrap">{msg.text}</p>

                  {/* Confidence Score Pill */}
                  {msg.confidenceScore !== undefined && !isUser && (
                    <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                      <span className="flex items-center space-x-1">
                        <Sparkles className="w-3 h-3 text-indigo-400" />
                        <span>AI Confidence: {(msg.confidenceScore * 100).toFixed(0)}%</span>
                      </span>
                      <span>{msg.timestamp}</span>
                    </div>
                  )}

                  {/* Source Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3 bg-slate-950/80 rounded-xl p-3 border border-slate-800">
                      <div className="flex items-center space-x-1 text-xs text-indigo-400 font-semibold mb-2">
                        <BookOpen className="w-3.5 h-3.5" />
                        <span>Verified Company Knowledge Sources ({msg.citations.length})</span>
                      </div>
                      <div className="space-y-2">
                        {msg.citations.map((cit) => (
                          <div
                            key={cit.id}
                            className="text-xs bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 text-slate-300"
                          >
                            <div className="flex justify-between font-medium text-indigo-300 mb-1">
                              <span>📄 {cit.documentName}</span>
                              <span className="text-[10px] text-slate-400">
                                Match: {(cit.relevanceScore * 100).toFixed(0)}%
                              </span>
                            </div>
                            <p className="italic text-slate-400 text-[11px]">"{cit.snippet}"</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Escalation Ticket Reference Card */}
                  {msg.isEscalated && msg.ticketId && (
                    <div className="mt-3 bg-amber-500/10 rounded-xl p-3 border border-amber-500/30 text-xs">
                      <div className="flex items-center justify-between text-amber-300 font-semibold mb-1">
                        <span className="flex items-center space-x-1.5">
                          <UserCheck className="w-4 h-4" />
                          <span>Escalation Ticket #{msg.ticketId}</span>
                        </span>
                        <span className="bg-amber-500 text-slate-950 font-bold px-2 py-0.5 rounded text-[10px]">
                          Pending Employee Response
                        </span>
                      </div>
                      <p className="text-slate-300 text-[11px]">
                        A company employee will review your question and respond in this chat thread shortly.
                      </p>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-1 shadow">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Thinking State */}
        {isBotThinking && (
          <div className="flex items-center space-x-3 text-slate-400 text-xs">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex items-center space-x-2 bg-slate-900 px-4 py-2.5 rounded-2xl border border-slate-800">
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-ping"></div>
              <span>Searching vector store & evaluating company knowledge...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Composer */}
      <div className="bg-slate-900 border-x border-b border-slate-800 rounded-b-2xl p-4">
        <form onSubmit={handleSubmit} className="flex items-center space-x-3">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask a question about policies, SLAs, specs, or company information..."
            className="flex-1 bg-slate-950 border border-slate-800 text-slate-100 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition placeholder-slate-500"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isBotThinking}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-5 py-3 rounded-xl transition flex items-center space-x-2 shadow-lg shadow-indigo-600/20"
          >
            <span>Ask</span>
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-500 px-1">
          <span>⚡ Powered by Vector Search + Automatic Employee Escalations</span>
          <span>Tip: Ask standard questions or trigger refusal with custom queries</span>
        </div>
      </div>
    </div>
  );
};
