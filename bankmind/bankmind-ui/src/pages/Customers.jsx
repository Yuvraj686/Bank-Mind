import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import { customersApi } from '../lib/api';
import { StageBadge, ScoreRing, LoadingSpinner, ErrorBanner } from '../components/ui/shared';

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stageFilter, setStageFilter] = useState('');
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const data = await customersApi.list(stageFilter || undefined);
      setCustomers(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [stageFilter]);

  return (
    <div className="flex min-h-screen bg-bg-base">
      <Sidebar />
      <main className="flex-1 pl-60 xl:pl-60 lg:pl-14 p-6">
        <div className="max-w-5xl space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-text-primary">Customers</h1>
              <p className="text-sm text-text-muted mt-0.5">{customers.length} customers</p>
            </div>
          </div>

          {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

          {/* Filters */}
          <div className="flex gap-2 flex-wrap">
            {['', 'lead', 'onboarding', 'active', 'dormant'].map(stage => (
              <button
                key={stage}
                onClick={() => setStageFilter(stage)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  stageFilter === stage
                    ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                    : 'border-bm-border text-text-muted hover:border-bm-border/80 hover:text-text-primary'
                }`}
              >
                {stage || 'All'}
              </button>
            ))}
          </div>

          {/* Grid */}
          {loading ? (
            <div className="flex justify-center py-12"><LoadingSpinner size={28} /></div>
          ) : customers.length === 0 ? (
            <div className="py-16 text-center">
              <div className="text-4xl mb-3">👥</div>
              <p className="text-text-muted text-sm">No customers. Run the demo to seed data.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
              {customers.map(c => (
                <div
                  key={c.id}
                  onClick={() => navigate(`/customers/${c.id}`)}
                  className="card cursor-pointer hover:border-accent-primary/50 hover:shadow-lg hover:shadow-accent-primary/5 transition-all duration-200"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-text-primary truncate">{c.name}</p>
                      <p className="text-xs text-text-muted mt-0.5">{c.occupation} · {c.city}</p>
                      <div className="mt-2">
                        <StageBadge stage={c.stage} />
                      </div>
                    </div>
                    {c.lead_score != null && <ScoreRing score={c.lead_score} size={44} />}
                  </div>
                  <div className="mt-3 pt-3 border-t border-bm-border flex justify-between text-xs text-text-muted">
                    <span>₹{(c.income_monthly || 0).toLocaleString('en-IN')}/mo</span>
                    {c.currently_processing && (
                      <span className="text-accent-primary flex items-center gap-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse" /> Processing
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
