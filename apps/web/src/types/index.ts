export type UserRole = 'customer' | 'admin' | 'employee';

export interface SourceCitation {
  id: string;
  documentId: string;
  documentName: string;
  pageNumber?: number;
  snippet: string;
  relevanceScore: number; // 0 to 1
}

export type MessageSender = 'user' | 'bot' | 'agent';

export interface ChatMessage {
  id: string;
  sender: MessageSender;
  text: string;
  timestamp: string;
  confidenceScore?: number;
  citations?: SourceCitation[];
  isRefused?: boolean;
  isEscalated?: boolean;
  ticketId?: string;
  agentName?: string;
}

export type DocumentStatus = 'uploading' | 'processing' | 'indexed' | 'failed';

export interface KnowledgeDocument {
  id: string;
  name: string;
  fileSize: string;
  fileType: 'pdf' | 'docx' | 'txt' | 'markdown';
  category: string;
  uploadDate: string;
  uploadedBy: string;
  status: DocumentStatus;
  chunksCount: number;
  tokensCount: number;
  vectorId?: string;
}

export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface EscalationTicket {
  id: string;
  customerName: string;
  customerEmail: string;
  query: string;
  chatHistory: ChatMessage[];
  reason: 'bot_refusal' | 'low_confidence' | 'user_requested' | 'complex_query';
  status: TicketStatus;
  priority: TicketPriority;
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
  resolutionNote?: string;
}

export interface SystemMetrics {
  totalQueries: number;
  botDeflectionRate: number; // percentage
  avgResponseTimeMs: number;
  totalDocumentsIndexed: number;
  activeEscalations: number;
  resolvedTicketsToday: number;
}
