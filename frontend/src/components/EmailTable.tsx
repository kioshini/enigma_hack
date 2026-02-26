import React from 'react';
import { Email } from '../types';

interface EmailTableProps {
  emails: Email[];
  loading: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  NEW: '#dbeafe',
  PROCESSED: '#dcfce7',
  NEEDS_OPERATOR: '#fef9c3',
  ESCALATED: '#fee2e2',
  CLOSED: '#f3f4f6',
};

const STATUS_BORDER: Record<string, string> = {
  NEW: '#3b82f6',
  PROCESSED: '#22c55e',
  NEEDS_OPERATOR: '#eab308',
  ESCALATED: '#ef4444',
  CLOSED: '#9ca3af',
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString();
}

function truncate(text: string | null, max = 80): string {
  if (!text) return '';
  return text.length > max ? text.slice(0, max) + '…' : text;
}

export const EmailTable: React.FC<EmailTableProps> = ({ emails, loading }) => {
  if (loading && emails.length === 0) {
    return <div className="loading">Loading emails...</div>;
  }

  if (emails.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📭</div>
        <h3>No emails found</h3>
        <p>Emails will appear here automatically when received via IMAP.</p>
        <p className="hint">This is a read-only view — data is populated by the email ingestion pipeline.</p>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Sender</th>
            <th>Subject</th>
            <th>Sentiment</th>
            <th>Complexity</th>
            <th>Confidence</th>
            <th>AI Response</th>
            <th>Received</th>
          </tr>
        </thead>
        <tbody>
          {emails.map((email) => (
            <tr
              key={email.id}
              style={{
                backgroundColor: STATUS_COLORS[email.status] || '#fff',
                borderLeft: `4px solid ${STATUS_BORDER[email.status] || '#ccc'}`,
              }}
            >
              <td>
                <span
                  className="status-badge"
                  style={{
                    backgroundColor: STATUS_BORDER[email.status] || '#ccc',
                  }}
                >
                  {email.status}
                </span>
              </td>
              <td className="cell-sender">{email.sender}</td>
              <td className="cell-subject" title={email.subject}>{truncate(email.subject, 60)}</td>
              <td>
                {email.sentiment && (
                  <span className={`sentiment sentiment-${email.sentiment}`}>
                    {email.sentiment}
                  </span>
                )}
              </td>
              <td>{email.complexity || '—'}</td>
              <td>{email.confidence ? `${(email.confidence * 100).toFixed(0)}%` : '—'}</td>
              <td className="cell-response" title={email.ai_response || ''}>
                {truncate(email.ai_response, 60)}
              </td>
              <td className="cell-date">{formatDate(email.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
