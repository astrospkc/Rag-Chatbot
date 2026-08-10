import React from 'react';
import { useApp } from '../../context/AppContext';
import {
  BarChart3,
  TrendingUp,
  Zap,
  BookOpen,
  UserCheck,
  ShieldCheck,
  Percent
} from 'lucide-react';

export const AnalyticsDashboard: React.FC = () => {
  const { metrics, documents, tickets } = useApp();

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 font-medium text-xs mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>Executive Performance Dashboard</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            RAG Knowledge & Deflection Analytics
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time statistics on automated bot query resolution vs. human employee escalations.
          </p>
        </div>

        <div className="bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-xs text-slate-400">
          Last Synced: <span className="text-white font-medium">Just now</span>
        </div>
      </div>

      {/* Grid Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-2">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold">
            <span>Bot Deflection Rate</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <Percent className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {metrics.botDeflectionRate}%
          </div>
          <div className="text-[11px] text-emerald-400 flex items-center gap-1 font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+3.2% vs last week</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-2">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold">
            <span>Avg Response Speed</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {metrics.avgResponseTimeMs} ms
          </div>
          <div className="text-[11px] text-indigo-400 font-medium">
            Sub-second vector lookup
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-2">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold">
            <span>Active Indexed Docs</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {documents.length} Files
          </div>
          <div className="text-[11px] text-purple-400 font-medium">
            {documents.reduce((acc, d) => acc + d.chunksCount, 0)} Total vector chunks
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-2">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold">
            <span>Active Escalations</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <UserCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {tickets.filter((t) => t.status !== 'resolved').length}
          </div>
          <div className="text-[11px] text-amber-400 font-medium">
            Handled by company employees
          </div>
        </div>
      </div>

      {/* Visual Workflow Architecture Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-indigo-400" />
          Enterprise Hybrid Query Flow Architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Step 1</span>
            <h3 className="text-sm font-semibold text-white">1. User Query & Vector Retrieval</h3>
            <p className="text-xs text-slate-400">
              Query is vectorized and matched against indexed company documents (PDFs, Policies) using similarity thresholds.
            </p>
          </div>

          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Step 2</span>
            <h3 className="text-sm font-semibold text-white">2. Guardrail & Confidence Check</h3>
            <p className="text-xs text-slate-400">
              If confidence score is below 70% or sensitive keywords match refusal rules, bot denies answering and generates ticket.
            </p>
          </div>

          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Step 3</span>
            <h3 className="text-sm font-semibold text-white">3. Employee Hand-Off</h3>
            <p className="text-xs text-slate-400">
              Company support employees receive the ticket with full context in their helpdesk, resolve the query, and update the knowledge base.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
