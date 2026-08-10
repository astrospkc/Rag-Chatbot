import React, { createContext, useContext, useState } from 'react';
import {
  UserRole,
  KnowledgeDocument,
  EscalationTicket,
  ChatMessage,
  SystemMetrics,
  SourceCitation
} from '../types';
import {
  INITIAL_DOCUMENTS,
  INITIAL_MESSAGES,
  INITIAL_TICKETS,
  INITIAL_METRICS
} from '../services/mockData';

interface AppContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
  documents: KnowledgeDocument[];
  addDocument: (doc: Omit<KnowledgeDocument, 'id' | 'uploadDate' | 'status' | 'chunksCount' | 'tokensCount'>) => void;
  deleteDocument: (id: string) => void;
  messages: ChatMessage[];
  sendMessage: (text: string) => void;
  tickets: EscalationTicket[];
  resolveTicket: (ticketId: string, resolutionNote: string) => void;
  assignTicket: (ticketId: string, agentName: string) => void;
  metrics: SystemMetrics;
  isBotThinking: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<UserRole>('customer');
  const [documents, setDocuments] = useState<KnowledgeDocument[]>(INITIAL_DOCUMENTS);
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [tickets, setTickets] = useState<EscalationTicket[]>(INITIAL_TICKETS);
  const [metrics, setMetrics] = useState<SystemMetrics>(INITIAL_METRICS);
  const [isBotThinking, setIsBotThinking] = useState(false);

  const addDocument = (newDoc: Omit<KnowledgeDocument, 'id' | 'uploadDate' | 'status' | 'chunksCount' | 'tokensCount'>) => {
    const docId = `doc-${Date.now()}`;
    const doc: KnowledgeDocument = {
      ...newDoc,
      id: docId,
      uploadDate: new Date().toISOString().replace('T', ' ').substring(0, 16),
      status: 'processing',
      chunksCount: Math.floor(Math.random() * 30) + 5,
      tokensCount: Math.floor(Math.random() * 15000) + 2000
    };

    setDocuments((prev) => [doc, ...prev]);

    // Simulate vectorization completion after 3.5 seconds
    setTimeout(() => {
      setDocuments((prev) =>
        prev.map((d) =>
          d.id === docId ? { ...d, status: 'indexed', vectorId: `vec-${Date.now()}` } : d
        )
      );
      setMetrics((prev) => ({
        ...prev,
        totalDocumentsIndexed: prev.totalDocumentsIndexed + 1
      }));
    }, 3500);
  };

  const deleteDocument = (id: string) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    setMetrics((prev) => ({
      ...prev,
      totalDocumentsIndexed: Math.max(0, prev.totalDocumentsIndexed - 1)
    }));
  };

  const sendMessage = (text: string) => {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsBotThinking(true);

    // Simulate RAG Pipeline Query Logic
    setTimeout(() => {
      setIsBotThinking(false);
      const lowerText = text.toLowerCase();

      // Check if trigger refusal or escalation scenario
      if (lowerText.includes('escrow') || lowerText.includes('human') || lowerText.includes('legal dispute') || lowerText.includes('custom failover')) {
        const ticketId = `TCK-${Math.floor(1000 + Math.random() * 9000)}`;
        const botRefusalMsg: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          sender: 'bot',
          text: `I've analyzed our indexed knowledge base, but this specific request requires human verification. I have automatically opened an escalation ticket (#${ticketId}) for a company employee to review and respond to you directly.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          confidenceScore: 0.35,
          isRefused: true,
          isEscalated: true,
          ticketId
        };

        const newTicket: EscalationTicket = {
          id: ticketId,
          customerName: 'Current Session User',
          customerEmail: 'user@clientorg.io',
          query: text,
          reason: lowerText.includes('escrow') ? 'bot_refusal' : 'low_confidence',
          status: 'open',
          priority: 'high',
          createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
          updatedAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
          chatHistory: [...messages, userMsg, botRefusalMsg]
        };

        setMessages((prev) => [...prev, botRefusalMsg]);
        setTickets((prev) => [newTicket, ...prev]);
        setMetrics((prev) => ({
          ...prev,
          totalQueries: prev.totalQueries + 1,
          activeEscalations: prev.activeEscalations + 1
        }));
      } else {
        // Standard high confidence RAG response
        const mockCitation: SourceCitation = {
          id: 'cit-1',
          documentId: 'doc-1',
          documentName: 'Company_Refund_Policy_2026.pdf',
          pageNumber: 3,
          snippet: 'Full refunds are issued within 14 business days of initial invoice date upon written request.',
          relevanceScore: 0.94
        };

        const botReply: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          sender: 'bot',
          text: `Based on section 3 of our verified knowledge base (${mockCitation.documentName}): We process requests according to our updated standard policy. Refunds are supported within 14 business days, with SLA guarantees applied automatically.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          confidenceScore: 0.94,
          citations: [mockCitation]
        };

        setMessages((prev) => [...prev, botReply]);
        setMetrics((prev) => ({
          ...prev,
          totalQueries: prev.totalQueries + 1
        }));
      }
    }, 1200);
  };

  const resolveTicket = (ticketId: string, resolutionNote: string) => {
    setTickets((prev) =>
      prev.map((t) =>
        t.id === ticketId
          ? {
              ...t,
              status: 'resolved',
              resolutionNote,
              updatedAt: new Date().toISOString().replace('T', ' ').substring(0, 16)
            }
          : t
      )
    );

    // Notify customer in chat if relevant
    const resolvedTicket = tickets.find((t) => t.id === ticketId);
    if (resolvedTicket) {
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          sender: 'agent',
          agentName: 'Employee Support Desk',
          text: `[UPDATE on Ticket ${ticketId}]: ${resolutionNote}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }

    setMetrics((prev) => ({
      ...prev,
      activeEscalations: Math.max(0, prev.activeEscalations - 1),
      resolvedTicketsToday: prev.resolvedTicketsToday + 1
    }));
  };

  const assignTicket = (ticketId: string, agentName: string) => {
    setTickets((prev) =>
      prev.map((t) =>
        t.id === ticketId
          ? {
              ...t,
              assignedTo: agentName,
              status: 'in_progress',
              updatedAt: new Date().toISOString().replace('T', ' ').substring(0, 16)
            }
          : t
      )
    );
  };

  return (
    <AppContext.Provider
      value={{
        role,
        setRole,
        documents,
        addDocument,
        deleteDocument,
        messages,
        sendMessage,
        tickets,
        resolveTicket,
        assignTicket,
        metrics,
        isBotThinking
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
