import { useEffect, useCallback } from 'react';
import { useDashboardStore } from '../store/dashboardStore';
import { useWebSocket } from '../hooks/useWebSocket';
import Sidebar from '../components/layout/Sidebar';
import KPITile from '../components/dashboard/KPITile';
import PipelineView from '../components/dashboard/PipelineView';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import DemoControls from '../components/dashboard/DemoControls';
import { ErrorBanner } from '../components/ui/shared';

export default function Dashboard() {
  const { kpis, pipeline, activityFeed, loading, error, demoComplete, fetchAll, prependFeedEntry, setDemoComplete, clearError } = useDashboardStore();

  // WebSocket handler
  const handleWsMessage = useCallback((msg) => {
    if (msg.event_type === 'agent_action') {
      prependFeedEntry({
        ...msg.data,
        id: msg.data.log_id,
        created_at: msg.timestamp,
        _new: true,
      });
      // Refresh KPIs and pipeline on stage changes
      useDashboardStore.getState().fetchKpis();
      useDashboardStore.getState().fetchPipeline();
    }
    if (msg.event_type === 'stage_change' || msg.event_type === 'kpi_update') {
      useDashboardStore.getState().fetchKpis();
      useDashboardStore.getState().fetchPipeline();
    }
    if (msg.event_type === 'demo_complete') {
      setDemoComplete(true);
      fetchAll();
    }
  }, [prependFeedEntry, setDemoComplete, fetchAll]);

  useWebSocket(handleWsMessage);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const kpiTiles = [
    { label: 'Total Leads',      value: kpis?.total_leads,         color: 'text-accent-primary',  suffix: '' },
    { label: 'Conversion Rate',  value: kpis?.conversion_rate,     color: 'text-accent-success',  suffix: '%' },
    { label: 'Active Customers', value: kpis?.active_customers,    color: 'text-accent-warning',  suffix: '' },
    { label: 'Adoption Rate',    value: kpis?.adoption_rate,       color: 'text-accent-purple',   suffix: '%' },
  ];

  return (
    <div className="flex min-h-screen bg-bg-base">
      <Sidebar />

      <main className="flex-1 pl-60 xl:pl-60 lg:pl-14 min-h-screen">
        <div className="p-6 space-y-6 max-w-[1600px]">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-text-primary">Banker Dashboard</h1>
              <p className="text-sm text-text-muted mt-0.5">Real-time AI agent activity monitor</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-accent-success animate-pulse" />
              <span className="text-xs text-text-muted">Live</span>
            </div>
          </div>

          {/* Error */}
          {error && <ErrorBanner message={error} onDismiss={clearError} />}

          {/* Demo Complete banner */}
          {demoComplete && (
            <div className="flex items-center justify-between bg-accent-success/10 border border-accent-success/30 text-accent-success rounded-xl px-5 py-3">
              <div className="flex items-center gap-3">
                <span className="text-xl">✅</span>
                <div>
                  <p className="font-semibold text-sm">Demo complete — all 4 agents ran</p>
                  <p className="text-xs opacity-80">All 5 customers processed through full lifecycle</p>
                </div>
              </div>
              <button onClick={() => setDemoComplete(false)} className="text-accent-success hover:opacity-70 text-lg">✕</button>
            </div>
          )}

          {/* KPI Tiles */}
          <div className="grid grid-cols-4 gap-4">
            {kpiTiles.map(tile => (
              <KPITile key={tile.label} {...tile} isLoading={loading && !kpis} />
            ))}
          </div>

          {/* Demo controls bar */}
          <DemoControls compact onAction={() => fetchAll()} />

          {/* Pipeline Kanban */}
          <section>
            <h2 className="text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wider">Customer Pipeline</h2>
            <PipelineView pipeline={pipeline} isLoading={loading && !pipeline} />
          </section>

          {/* Activity Feed */}
          <section className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-text-primary">Live Activity Feed</h2>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-accent-success animate-pulse" />
                <span className="text-xs text-text-muted">WebSocket</span>
              </div>
            </div>
            <ActivityFeed entries={activityFeed} isLoading={loading && !activityFeed.length} />
          </section>
        </div>
      </main>
    </div>
  );
}
