import { EmailListResponse, Stats } from './types';

const API_BASE = '/api/v1';

export async function fetchEmails(
  status?: string,
  search?: string,
  limit = 100,
  offset = 0
): Promise<EmailListResponse> {
  const params = new URLSearchParams();
  if (status && status !== 'ALL') params.set('status', status);
  if (search) params.set('search', search);
  params.set('limit', String(limit));
  params.set('offset', String(offset));

  const res = await fetch(`${API_BASE}/emails?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch emails');
  return res.json();
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/emails/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export function getExportUrl(status?: string, search?: string): string {
  const params = new URLSearchParams();
  if (status && status !== 'ALL') params.set('status', status);
  if (search) params.set('search', search);
  return `${API_BASE}/emails/export/csv?${params.toString()}`;
}
