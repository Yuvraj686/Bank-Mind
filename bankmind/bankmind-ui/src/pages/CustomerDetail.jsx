import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import ProfilePanel from '../components/customers/ProfilePanel';
import ChatWindow from '../components/customers/ChatWindow';
import AgentLogPanel from '../components/customers/AgentLogPanel';
import { customersApi, agentsApi } from '../lib/api';
import { LoadingSpinner, ErrorBanner, StageBadge } from '../components/ui/shared';

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [cust, convs, agentLogs] = await Promise.all([
        customersApi.get(id),
        customersApi.getConversations(id),
        agentsApi.logsForCustomer(id),
      ]);
      setCustomer(cust);
      setConversations(convs);
      setLogs(agentLogs);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleRunAgent = async () => {
    setRunning(true);
    try {
      await agentsApi.run(id);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-bg-base">
      <Sidebar />

      <main className="flex-1 pl-60 xl:pl-60 lg:pl-14 flex flex-col">
        {/* Top bar */}
        <div className="h-14 border-b border-bm-border flex items-center px-6 gap-4 bg-bg-surface/50">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-text-muted hover:text-text-primary text-sm flex items-center gap-1.5 transition-colors"
          >
            ← Back
          </button>
          {customer && (
            <>
              <span className="text-text-muted">/</span>
              <span className="text-sm font-medium text-text-primary">{customer.name}</span>
              <StageBadge stage={customer.stage} />
              {customer.currently_processing && (
                <div className="flex items-center gap-1.5 text-xs text-accent-primary">
                  <div className="processing-dot" />
                  Processing...
                </div>
              )}
            </>
          )}
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={handleRunAgent}
              disabled={running || customer?.currently_processing}
              className="btn-primary text-xs disabled:opacity-50"
            >
              {running ? <><LoadingSpinner size={14} /> Running...</> : '▶ Run Agent'}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="p-4">
            <ErrorBanner message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {/* 3-panel layout */}
        {loading ? (
          <div className="flex items-center justify-center flex-1">
            <LoadingSpinner size={32} />
          </div>
        ) : customer ? (
          <div className="flex flex-1 overflow-hidden">
            {/* Left: Profile 25% */}
            <div className="w-64 xl:w-72 flex-shrink-0 border-r border-bm-border overflow-y-auto p-4">
              <ProfilePanel customer={customer} />
            </div>

            {/* Center: Chat 45% */}
            <div className="flex-1 border-r border-bm-border flex flex-col overflow-hidden">
              <div className="px-4 py-3 border-b border-bm-border">
                <h3 className="text-sm font-semibold text-text-primary">Conversation</h3>
                <p className="text-xs text-text-muted">{conversations.length} messages</p>
              </div>
              <div className="flex-1 overflow-y-auto">
                <ChatWindow
                  conversations={conversations}
                  customerName={customer.name}
                />
              </div>
            </div>

            {/* Right: Agent Logs 30% */}
            <div className="w-80 xl:w-96 flex-shrink-0 overflow-y-auto p-4">
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-text-primary">Agent Activity</h3>
                <p className="text-xs text-text-muted">{logs.length} actions logged</p>
              </div>
              <AgentLogPanel logs={logs} onOverride={load} />
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center flex-1 text-text-muted">Customer not found</div>
        )}
      </main>
    </div>
  );
}
