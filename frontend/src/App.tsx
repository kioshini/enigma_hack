import { useState, useEffect, useCallback } from 'react';
import { Email, StatusFilter, Stats } from './types';
import { fetchEmails, fetchStats, getExportUrl } from './api';
import { EmailTable } from './components/EmailTable';
import { StatusFilterBar } from './components/StatusFilter';
import { ExportButton } from './components/ExportButton';

const POLL_INTERVAL = 5000;

function App() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<Stats | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const loadData = useCallback(async () => {
    try {
      const [emailData, statsData] = await Promise.all([
        fetchEmails(statusFilter, search || undefined),
        fetchStats(),
      ]);
      setEmails(emailData.emails);
      setTotal(emailData.total);
      setStats(statsData);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, search]);

  // Auto-refresh every 5 seconds
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [loadData]);

  const exportUrl = getExportUrl(statusFilter, search || undefined);

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>
            <span className="logo">🤖</span>
            Email AI Support
          </h1>
          <span className="subtitle">Automated email processing pipeline</span>
        </div>
        <div className="header-right">
          <span className="update-indicator" title="Auto-refreshes every 5 seconds">
            <span className="pulse"></span>
            Live
          </span>
          <span className="last-update">
            Updated: {lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </header>

      <main className="main">
        <div className="toolbar">
          <StatusFilterBar current={statusFilter} onChange={setStatusFilter} stats={stats} />
          <div className="toolbar-right">
            <input
              type="text"
              className="search-input"
              placeholder="Search sender or subject..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <ExportButton exportUrl={exportUrl} />
          </div>
        </div>

        <div className="info-bar">
          <span>
            Showing <strong>{emails.length}</strong> of <strong>{total}</strong> emails
          </span>
          {stats && (
            <span className="pipeline-info">
              Pipeline: Email → IMAP Polling → ML Analysis → Database → This Dashboard
            </span>
          )}
        </div>

        <EmailTable emails={emails} loading={loading} />
      </main>

      <footer className="footer">
        <p>Read-only dashboard — All data is ingested automatically via IMAP email pipeline</p>
      </footer>
    </div>
  );
}

export default App;
