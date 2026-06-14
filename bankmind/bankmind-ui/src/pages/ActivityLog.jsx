import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import { agentsApi } from '../lib/api';
import { AgentBadge, StageBadge, ConfidenceBar, LoadingSpinner, ErrorBanner, formatDateTime } from '../components/ui/shared';

const AGENT_OPTIONS = ['', 'acquisition', 'onboarding', 'adoption', 'life_event'];

function LogRow({ log, onClick }) {
  return (
    <tr
      onClick={() => onClick(log)}
      className={`
        cursor-pointer hover:bg-bg-elevated/50 transition-colors border-b border-bm-border
        ${log.was_overridden ? 'border-l-2 border-l-accent-warning' : ''}
      `}
    >
      <td className="px-4 py-3"><AgentBadge agent={log.agent_name} /></td>
      <td className="px-4 py-3 text-sm text-text-primary font-medium">{log.customer_name}</td>
      <td className="px-4 py-3 text-xs mono text-text-muted">{log.action?.replace(/_/g, ' ')}</td>
      <td className="px-4 py-3">
        {log.stage_before !== log.stage_after && log.stage_after
          ? <div className="flex items-center gap-1"><StageBadge stage={log.stage_before} /><span className="text-text-muted">→</span><StageBadge stage={log.stage_after} /></div>
          : <StageBadge stage={log.stage_before} />
        }
      </td>
      <td className="px-4 py-3"><ConfidenceBar confidence={log.confidence} /></td>
      <td className="px-4 py-3 text-xs mono text-text-muted">{formatDateTime(log.created_at)}</td>
      <td className="px-4 py-3">
        {log.was_overridden && <span className="text-xs text-accent-warning">⚠ Overridden</span>}
      </td>
    </tr>
  );
}

function LogDetailDrawer({ log, onClose }) {
  if (!log) return null;
  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-bg-surface border-l border-bm-border shadow-2xl z-50 flex flex-col animate-slide-in">
      <div className="flex items-center justify-between px-5 py-4 border-b border-bm-border">
        <h3 className="text-sm font-semibold text-text-primary">Log Detail</h3>
        <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg">✕</button>
      </div>
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        <div className="space-y-3 text-xs">
          <div className="flex justify-between"><span className="text-text-muted">Agent</span><AgentBadge agent={log.agent_name} /></div>
          <div className="flex justify-between"><span className="text-text-muted">Customer</span><span className="text-text-primary font-medium">{log.customer_name}</span></div>
          <div className="flex justify-between"><span className="text-text-muted">Action</span><span className="mono text-text-secondary">{log.action}</span></div>
          <div className="flex justify-between"><span className="text-text-muted">Date</span><span className="mono text-text-muted">{formatDateTime(log.created_at)}</span></div>
          {log.confidence != null && (
            <div><span className="text-text-muted block mb-1">Confidence</span><ConfidenceBar confidence={log.confidence} /></div>
          )}
        </div>
        {log.message_sent && (
          <div>
            <p className="text-xs font-medium text-text-muted mb-2">Message Sent</p>
            <div className="bg-bg-elevated rounded-lg p-3 text-xs text-text-secondary leading-relaxed">{log.message_sent}</div>
          </div>
        )}
        {log.reasoning && (
          <div>
            <p className="text-xs font-medium text-text-muted mb-2">Reasoning</p>
            <div className="bg-bg-elevated rounded-lg p-3 text-xs text-text-secondary leading-relaxed">{log.reasoning}</div>
          </div>
        )}
        {log.was_overridden && (
          <div className="bg-accent-warning/5 border border-accent-warning/20 rounded-lg p-3">
            <p className="text-xs text-accent-warning font-medium mb-1">Overridden</p>
            <p className="text-xs text-text-muted">By: {log.override_by}</p>
            {log.override_note && <p className="text-xs text-text-secondary mt-1">{log.override_note}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ActivityLog() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [agentFilter, setAgentFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);
  const navigate = useNavigate();

  const load = async (p = page) => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: p, page_size: 25 };
      if (agentFilter) params.agent_name = agentFilter;
      const result = await agentsApi.logs(params);
      const filtered = search
        ? result.logs.filter(l => l.customer_name?.toLowerCase().includes(search.toLowerCase()))
        : result.logs;
      setLogs(filtered);
      setTotal(result.total);
      setPages(result.pages);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); setPage(1); }, [agentFilter]);
  useEffect(() => { load(page); }, [page]);

  return (
    <div className="flex min-h-screen bg-bg-base">
      <Sidebar />
      <main className="flex-1 pl-60 xl:pl-60 lg:pl-14 p-6">
        <div className="max-w-6xl space-y-5">
          <div>
            <h1 className="text-xl font-bold text-text-primary">Activity Log</h1>
            <p className="text-sm text-text-muted mt-0.5">Complete history of all agent actions · {total} total</p>
          </div>

          {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

          {/* Filters */}
          <div className="flex items-center gap-3 flex-wrap">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search customer..."
              className="input w-48 text-xs"
            />
            <select
              value={agentFilter}
              onChange={e => setAgentFilter(e.target.value)}
              className="input w-40 text-xs"
            >
              {AGENT_OPTIONS.map(a => (
                <option key={a} value={a}>{a || 'All agents'}</option>
              ))}
            </select>
            <button onClick={() => load(page)} className="btn-ghost text-xs">↻ Refresh</button>
          </div>

          {/* Table */}
          <div className="card overflow-hidden p-0">
            {loading ? (
              <div className="flex justify-center py-12"><LoadingSpinner size={28} /></div>
            ) : logs.length === 0 ? (
              <div className="py-16 text-center">
                <p className="text-text-muted text-sm">No activity yet. Run the demo to generate logs.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-bm-border text-xs text-text-muted uppercase tracking-wider">
                      <th className="px-4 py-3 text-left">Agent</th>
                      <th className="px-4 py-3 text-left">Customer</th>
                      <th className="px-4 py-3 text-left">Action</th>
                      <th className="px-4 py-3 text-left">Stage</th>
                      <th className="px-4 py-3 text-left">Confidence</th>
                      <th className="px-4 py-3 text-left">Time</th>
                      <th className="px-4 py-3 text-left">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map(log => (
                      <LogRow key={log.id} log={log} onClick={setSelectedLog} />
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="flex items-center justify-between">
              <span className="text-xs text-text-muted">Page {page} of {pages}</span>
              <div className="flex gap-2">
                <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="btn-ghost text-xs disabled:opacity-40">← Prev</button>
                <button disabled={page >= pages} onClick={() => setPage(p => p + 1)} className="btn-ghost text-xs disabled:opacity-40">Next →</button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Detail drawer */}
      {selectedLog && <LogDetailDrawer log={selectedLog} onClose={() => setSelectedLog(null)} />}
    </div>
  );
}
