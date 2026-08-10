import { KnowledgeDocument, EscalationTicket, ChatMessage, SystemMetrics } from '../types';

export const INITIAL_DOCUMENTS: KnowledgeDocument[] = [
  {
    id: 'doc-1',
    name: 'Company_Refund_Policy_2026.pdf',
    fileSize: '2.4 MB',
    fileType: 'pdf',
    category: 'Billing & Payments',
    uploadDate: '2026-08-01 10:14',
    uploadedBy: 'Admin (Sarah Vance)',
    status: 'indexed',
    chunksCount: 42,
    tokensCount: 18400,
    vectorId: 'vec-001-rf'
  },
  {
    id: 'doc-2',
    name: 'Product_Architecture_Whitepaper.pdf',
    fileSize: '5.1 MB',
    fileType: 'pdf',
    category: 'Engineering & API',
    uploadDate: '2026-08-04 14:22',
    uploadedBy: 'Admin (Sarah Vance)',
    status: 'indexed',
    chunksCount: 118,
    tokensCount: 54200,
    vectorId: 'vec-002-arch'
  },
  {
    id: 'doc-3',
    name: 'SLA_Enterprise_Support_Terms.docx',
    fileSize: '840 KB',
    fileType: 'docx',
    category: 'Legal & SLA',
    uploadDate: '2026-08-08 09:05',
    uploadedBy: 'Legal Team',
    status: 'indexed',
    chunksCount: 18,
    tokensCount: 9100,
    vectorId: 'vec-003-sla'
  },
  {
    id: 'doc-4',
    name: 'Internal_Employee_Onboarding_Guide.md',
    fileSize: '320 KB',
    fileType: 'markdown',
    category: 'Human Resources',
    uploadDate: '2026-08-10 11:30',
    uploadedBy: 'HR Lead',
    status: 'processing',
    chunksCount: 12,
    tokensCount: 4300
  }
];

export const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: 'msg-1',
    sender: 'bot',
    text: 'Hello! I am your AI Knowledge Assistant. How can I help you today with company policies, SLAs, or technical services?',
    timestamp: '10:00 AM',
    confidenceScore: 0.99
  }
];

export const INITIAL_TICKETS: EscalationTicket[] = [
  {
    id: 'TCK-8821',
    customerName: 'Alex Rivera',
    customerEmail: 'alex.rivera@clientcorp.io',
    query: 'What is the custom custom custom enterprise SLA clause for multi-region failover timing?',
    reason: 'low_confidence',
    status: 'open',
    priority: 'high',
    createdAt: '2026-08-10 14:15',
    updatedAt: '2026-08-10 14:15',
    chatHistory: [
      {
        id: 'hist-1',
        sender: 'user',
        text: 'What is the custom enterprise SLA clause for multi-region failover timing?',
        timestamp: '14:14 AM'
      },
      {
        id: 'hist-2',
        sender: 'bot',
        text: 'I am sorry, I could not find a specific multi-region failover timing guarantee in the standard indexed public documents. Let me connect you with an employee.',
        timestamp: '14:15 AM',
        confidenceScore: 0.32,
        isRefused: true,
        isEscalated: true
      }
    ]
  },
  {
    id: 'TCK-8820',
    customerName: 'Elena Rostova',
    customerEmail: 'elena@fintechtech.com',
    query: 'Requesting custom wire transfer instructions for invoice #INV-9021',
    reason: 'bot_refusal',
    status: 'in_progress',
    priority: 'urgent',
    assignedTo: 'Marcus Brody (Support)',
    createdAt: '2026-08-10 12:40',
    updatedAt: '2026-08-10 13:00',
    chatHistory: [
      {
        id: 'hist-3',
        sender: 'user',
        text: 'Requesting custom wire transfer instructions for invoice #INV-9021',
        timestamp: '12:40 PM'
      },
      {
        id: 'hist-4',
        sender: 'bot',
        text: 'For security and compliance reasons, I am automated to refuse sharing raw wire routing details directly in chat without human verification.',
        timestamp: '12:40 PM',
        isRefused: true,
        isEscalated: true
      }
    ]
  }
];

export const INITIAL_METRICS: SystemMetrics = {
  totalQueries: 1482,
  botDeflectionRate: 88.4,
  avgResponseTimeMs: 420,
  totalDocumentsIndexed: 4,
  activeEscalations: 2,
  resolvedTicketsToday: 19
};
