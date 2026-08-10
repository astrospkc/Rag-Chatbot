import React from 'react';
import { useApp } from '../../context/AppContext';
import { UserRole } from '../../types';
import {
  MessageSquare,
  FileText,
  UserCheck,
  BarChart3,
  Bot,
  ShieldCheck,
  Layers,
  Sparkles
} from 'lucide-react';

export const AppHeader: React.FC<{ activeTab: string; setActiveTab: (tab: string) => void }> = ({
  activeTab,
  setActiveTab
}) => {
  const { role, setRole, tickets, documents } = useApp();

  const handleRoleChange = (newRole: UserRole) => {
    setRole(newRole);
    if (newRole === 'customer') setActiveTab('chat');
    else if (newRole === 'admin') setActiveTab('documents');
    else if (newRole === 'employee') setActiveTab('tickets');
  };

  const openTicketsCount = tickets.filter((t) => t.status === 'open').length;

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 shadow-lg py-1">
      <div className="max-w-[96rem] mx-auto px-6 sm:px-8 lg:px-10">
        <div className="flex items-center justify-between min-h-[4.5rem] gap-6">
          {/* Logo & Platform Badge */}
          <div className="flex items-center space-x-4 shrink-0">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="font-bold text-lg text-white tracking-tight">Enterprise RAG Assistant</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Sparkles className="w-3 h-3 mr-1" />
                  Hybrid Human-in-the-Loop
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Contextual Knowledge Engine & Escalation Hub</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden lg:flex items-center space-x-2 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800/80">
            <button
              onClick={() => {
                setRole('customer');
                setActiveTab('chat');
              }}
              className={`flex items-center space-x-2.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'chat'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Customer Chat</span>
            </button>

            <button
              onClick={() => {
                setRole('admin');
                setActiveTab('documents');
              }}
              className={`flex items-center space-x-2.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'documents'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Company Documents</span>
              <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full text-[10px]">
                {documents.length}
              </span>
            </button>

            <button
              onClick={() => {
                setRole('employee');
                setActiveTab('tickets');
              }}
              className={`flex items-center space-x-2.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'tickets'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <UserCheck className="w-4 h-4" />
              <span>Employee Helpdesk</span>
              {openTicketsCount > 0 && (
                <span className="bg-amber-500 text-slate-950 font-bold px-2 py-0.5 rounded-full text-[10px] animate-pulse">
                  {openTicketsCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center space-x-2.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'analytics'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </button>
          </nav>

          {/* Role Switcher Pill */}
          <div className="flex items-center space-x-4 shrink-0">
            <div className="hidden sm:flex items-center bg-slate-950 px-3.5 py-2 rounded-xl border border-slate-800 text-xs shadow-inner">
              <Layers className="w-4 h-4 text-slate-400 mr-2" />
              <span className="text-slate-400 mr-2 font-medium">Role:</span>
              <select
                value={role}
                onChange={(e) => handleRoleChange(e.target.value as UserRole)}
                className="bg-transparent text-indigo-400 font-semibold focus:outline-none cursor-pointer pr-1"
              >
                <option value="customer">User / Customer</option>
                <option value="admin">Company Owner / Admin</option>
                <option value="employee">Support Employee</option>
              </select>
            </div>

            <div className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20 shadow-sm">
              <ShieldCheck className="w-4 h-4" />
              <span className="font-semibold whitespace-nowrap">Vector Store Ready</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
