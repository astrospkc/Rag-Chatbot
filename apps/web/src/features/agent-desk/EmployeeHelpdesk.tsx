import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  UserCheck,
  CheckCircle,
  Send,
  MessageSquare,
  Inbox
} from 'lucide-react';

export const EmployeeHelpdesk: React.FC = () => {
  const { tickets, resolveTicket, assignTicket } = useApp();
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(
    tickets.length > 0 ? tickets[0].id : null
  );
  const [resolutionInput, setResolutionInput] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'open' | 'resolved'>('all');

  const selectedTicket = tickets.find((t) => t.id === selectedTicketId);

  const handleResolve = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTicketId || !resolutionInput.trim()) return;
    resolveTicket(selectedTicketId, resolutionInput.trim());
    setResolutionInput('');
  };

  const filteredTickets = tickets.filter((t) => {
    if (statusFilter === 'open') return t.status === 'open' || t.status === 'in_progress';
    if (statusFilter === 'resolved') return t.status === 'resolved';
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Employee Desk Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-amber-400 font-medium text-xs mb-1">
            <UserCheck className="w-4 h-4" />
            <span>Human-in-the-Loop Support Desk</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Employee Refusal & Escalation Inbox
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Review customer queries refused by the AI chatbot due to guardrails or low retrieval confidence.
          </p>
        </div>

        {/* Status Pills */}
        <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition ${
              statusFilter === 'all'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All Tickets ({tickets.length})
          </button>
          <button
            onClick={() => setStatusFilter('open')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition ${
              statusFilter === 'open'
                ? 'bg-amber-500 text-slate-950 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Open ({tickets.filter((t) => t.status !== 'resolved').length})
          </button>
          <button
            onClick={() => setStatusFilter('resolved')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition ${
              statusFilter === 'resolved'
                ? 'bg-emerald-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Resolved ({tickets.filter((t) => t.status === 'resolved').length})
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Ticket List */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 px-2">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Inbox className="w-4 h-4 text-indigo-400" />
              Escalated Queries Queue
            </span>
          </div>

          {filteredTickets.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs">
              No tickets matching current filter.
            </div>
          ) : (
            filteredTickets.map((t) => {
              const isSelected = t.id === selectedTicketId;
              return (
                <div
                  key={t.id}
                  onClick={() => setSelectedTicketId(t.id)}
                  className={`p-4 rounded-xl border transition cursor-pointer space-y-2 ${
                    isSelected
                      ? 'bg-slate-800 border-indigo-500 shadow-md'
                      : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-indigo-300">{t.id}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        t.status === 'resolved'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : t.status === 'in_progress'
                          ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {t.status.replace('_', ' ')}
                    </span>
                  </div>

                  <p className="text-xs text-slate-200 font-medium line-clamp-2">{t.query}</p>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                    <span>👤 {t.customerName}</span>
                    <span>{t.createdAt}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Ticket Detail & Resolution Console */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          {selectedTicket ? (
            <>
              {/* Detail Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center space-x-2 text-xs font-mono text-indigo-400">
                    <span>Ticket #{selectedTicket.id}</span>
                    <span>•</span>
                    <span className="text-slate-400">Priority: {selectedTicket.priority.toUpperCase()}</span>
                  </div>
                  <h2 className="text-lg font-bold text-white mt-1">{selectedTicket.query}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Customer: {selectedTicket.customerName} ({selectedTicket.customerEmail})
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  {selectedTicket.status !== 'resolved' && (
                    <button
                      onClick={() => assignTicket(selectedTicket.id, 'Marcus Brody (Support)')}
                      className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-2 rounded-xl border border-slate-700 transition"
                    >
                      Assign to Me
                    </button>
                  )}
                </div>
              </div>

              {/* Chat History Snippet */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <MessageSquare className="w-4 h-4 text-indigo-400" />
                  Bot Conversation History Context
                </h3>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 max-h-64 overflow-y-auto space-y-3">
                  {selectedTicket.chatHistory.map((item, idx) => (
                    <div
                      key={idx}
                      className={`text-xs p-3 rounded-lg border ${
                        item.sender === 'user'
                          ? 'bg-indigo-950/40 border-indigo-800/40 text-indigo-200'
                          : 'bg-slate-900 border-slate-800 text-slate-300'
                      }`}
                    >
                      <div className="font-semibold text-[11px] mb-1 text-slate-400">
                        {item.sender === 'user' ? '👤 Customer' : '🤖 AI Bot Refusal'}
                      </div>
                      <p>{item.text}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Resolution Form or Resolution Card */}
              {selectedTicket.status === 'resolved' ? (
                <div className="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-xl space-y-2">
                  <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs">
                    <CheckCircle className="w-4 h-4" />
                    <span>Ticket Resolved by Support Employee</span>
                  </div>
                  <p className="text-xs text-slate-200 italic">
                    "{selectedTicket.resolutionNote}"
                  </p>
                </div>
              ) : (
                <form onSubmit={handleResolve} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">
                      Employee Response / Knowledge Base Correction Note
                    </label>
                    <textarea
                      rows={4}
                      value={resolutionInput}
                      onChange={(e) => setResolutionInput(e.target.value)}
                      placeholder="Type official response to customer or document correction note..."
                      className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-xl p-3 text-xs focus:outline-none focus:border-indigo-500 transition"
                    ></textarea>
                  </div>

                  <button
                    type="submit"
                    disabled={!resolutionInput.trim()}
                    className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-xl transition flex items-center space-x-2 text-xs shadow-lg shadow-emerald-600/20"
                  >
                    <Send className="w-4 h-4" />
                    <span>Resolve & Send Response to Customer</span>
                  </button>
                </form>
              )}
            </>
          ) : (
            <div className="p-12 text-center text-slate-500 text-xs">
              Select a ticket from the left queue to view context and respond.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
