export interface Email {
  id: string;
  sender: string;
  subject: string;
  body: string;
  status: string;
  complexity: string | null;
  sentiment: string | null;
  ai_response: string | null;
  confidence: number | null;
  created_at: string;
}

export interface EmailListResponse {
  emails: Email[];
  total: number;
}

export interface Stats {
  total: number;
  new: number;
  processed: number;
  needs_operator: number;
  escalated: number;
  closed: number;
}

export type StatusFilter = 'ALL' | 'NEW' | 'PROCESSED' | 'NEEDS_OPERATOR' | 'ESCALATED' | 'CLOSED';
