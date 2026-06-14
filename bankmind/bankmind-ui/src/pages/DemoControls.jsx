import { useState, useEffect, useCallback } from 'react';
import Sidebar from '../components/layout/Sidebar';
import DemoControls from '../components/dashboard/DemoControls';
import { useWebSocket } from '../hooks/useWebSocket';
import { demoApi } from '../lib/api';
import { LoadingSpinner } from '../components/ui/shared';

export default function DemoPage() {
  const [demoState, setDemoState] = useState({ status: 'idle', step: null, progress: 0 });
  const [logs, setLogs] = useState([]);

  const refreshState = async () => {
    try {
      const state = await demoApi.state();
      setDemoState(state || { status: 'idle', step: null, progress: 0 });
    } catch (_) {}
  };

  const handleWsMessage = useCallback((msg) => {
    if (msg.event_type === 'demo_progress') {
      setDemoState(s => ({ ...s, step: msg.data.step, status: msg.data.status === 'complete' ? 'complete' : 'running' }));
      setLogs(l => [{
        time: new Date().toLocaleTimeString(),
        message: `${msg.data.step?.toUpperCase()} — ${msg.data.status}`,
        customer: msg.data.customer_name,
      }, ...l.slice(0, 19)]);
    }
    if (msg.event_type === 'agent_action') {
      setLogs(l => [{
        time: new Date().toLocaleTimeString(),
        message: `${msg.data.agent?.toUpperCase()} → ${msg.data.action?.replace(/_/g, ' ')}`,
        customer: msg.data.customer_name,
        agent: msg.data.agent,
      }, ...l.slice(0, 19)]);
    }
    if (msg.event_type === 'demo_complete') {
      setDemoState({ status: 'complete', step: 'done', progress: 100 });
    }
  }, []);

  useWebSocket(handleWsMessage);

  useEffect(() => {
    refreshState();
  }, []);

  const AGENT_COLORS = {
    acquisition: 'text-accent-primary',
    onboarding:  'text-accent-warning',
    adoption:    'text-accent-success',
    life_event:  'text-accent-purple',
  };

  return (
    <div className="flex min-h-screen bg-bg-base">
      <Sidebar />
      <main className="flex-1 pl-60 xl:pl-60 lg:pl-14 p-6">
        <div className="max-w-3xl space-y-6">
          <div>
            <h1 className="text-xl font-bold text-text-primary">Demo Controls</h1>
            <p className="text-sm text-text-muted mt-0.5">Run the full customer journey simulation with live agent updates</p>
          </div>

          {/* Full demo controls panel */}
          <DemoControls demoState={demoState} onAction={refreshState} />

          {/* Instructions */}
          <div className="card space-y-3">
            <h3 className="text-sm font-semibold text-text-primary">How to run the demo</h3>
            <ol className="space-y-2 text-xs text-text-secondary">
              <li className="flex gap-3"><span className="text-accent-primary font-bold">1.</span><span><strong className="text-text-primary">Seed Data</strong> — Creates 5 demo customers with 60 transactions each and life-event patterns</span></li>
              <li className="flex gap-3"><span className="text-accent-primary font-bold">2.</span><span><strong className="text-text-primary">Run Demo</strong> — All 4 AI agents run sequentially (Acquisition → Onboarding → Adoption → Life-Event)</span></li>
              <li className="flex gap-3"><span className="text-accent-primary font-bold">3.</span><span><strong className="text-text-primary">Watch live</strong> — Go to Dashboard to see the live activity feed update in real-time via WebSocket</span></li>
              <li className="flex gap-3"><span className="text-accent-primary font-bold">4.</span><span><strong className="text-text-primary">Explore</strong> — Click any customer card to see the 3-panel detail view with chat, agent logs, and override options</span></li>
              <li className="flex gap-3"><span className="text-accent-primary font-bold">5.</span><span><strong className="text-text-primary">Reset</strong> — Click Reset to wipe all data and start fresh anytime</span></li>
            </ol>
          </div>

          {/* Live event log */}
          {logs.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-text-primary mb-3">Live Event Stream</h3>
              <div className="space-y-1.5 overflow-y-auto max-h-64">
                {logs.map((log, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs py-1.5 border-b border-bm-border last:border-0">
                    <span className="mono text-text-muted flex-shrink-0">{log.time}</span>
                    {log.customer && <span className="text-text-secondary flex-shrink-0">{log.customer}</span>}
                    <span className={`font-medium ${AGENT_COLORS[log.agent] || 'text-text-primary'}`}>{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
