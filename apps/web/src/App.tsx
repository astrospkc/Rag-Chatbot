import React, { useState } from 'react';
import { AppProvider } from './context/AppContext';
import { AppHeader } from './components/layout/AppHeader';
import { ChatWindow } from './features/chat/ChatWindow';
import { DocumentManagement } from './features/documents/DocumentManagement';
import { EmployeeHelpdesk } from './features/agent-desk/EmployeeHelpdesk';
import { AnalyticsDashboard } from './features/analytics/AnalyticsDashboard';

const MainContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-indigo-500 selection:text-white">
      {/* Universal Enterprise Navigation Bar */}
      <AppHeader activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Dynamic View Router based on Navigation & Role */}
      <main className="pb-12">
        {activeTab === 'chat' && <ChatWindow />}
        {activeTab === 'documents' && <DocumentManagement />}
        {activeTab === 'tickets' && <EmployeeHelpdesk />}
        {activeTab === 'analytics' && <AnalyticsDashboard />}
      </main>
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <MainContent />
    </AppProvider>
  );
}
