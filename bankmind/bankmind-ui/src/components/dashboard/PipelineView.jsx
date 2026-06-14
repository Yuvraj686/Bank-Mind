import { useNavigate } from 'react-router-dom';
import { StageBadge, ScoreRing, LoadingSpinner } from '../ui/shared';

const STAGE_ORDER = ['lead', 'onboarding', 'active', 'dormant'];

const STAGE_CONFIG = {
  lead:       { label: 'Lead',       color: 'border-accent-primary/40',  headerBg: 'bg-accent-primary/5' },
  onboarding: { label: 'Onboarding', color: 'border-accent-warning/40',  headerBg: 'bg-accent-warning/5' },
  active:     { label: 'Active',     color: 'border-accent-success/40',  headerBg: 'bg-accent-success/5' },
  dormant:    { label: 'Dormant',    color: 'border-text-muted/30',      headerBg: 'bg-text-muted/5' },
};

function CustomerCard({ customer }) {
  const navigate = useNavigate();
  const featuresAdopted = customer.features_adopted || {};
  const adoptedCount = Object.values(featuresAdopted).filter(Boolean).length;
  const totalFeatures = Object.keys(featuresAdopted).length || 5;

  return (
    <div
      onClick={() => navigate(`/customers/${customer.id}`)}
      className={`
        bg-bg-elevated border border-bm-border rounded-lg p-3 cursor-pointer
        hover:border-accent-primary/50 hover:bg-bg-elevated/80 transition-all duration-150 group
        ${customer.currently_processing ? 'border-accent-primary/60' : ''}
      `}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-text-primary group-hover:text-accent-primary transition-colors truncate">
            {customer.name}
          </p>
          <p className="text-xs text-text-muted mt-0.5 truncate">{customer.occupation} · {customer.city}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {customer.currently_processing && (
            <div className="processing-dot" title="Agent processing..." />
          )}
          {customer.lead_score != null && (
            <ScoreRing score={customer.lead_score} size={36} />
          )}
        </div>
      </div>
      {customer.stage === 'active' && totalFeatures > 0 && (
        <div className="mt-2">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-text-muted">Features</span>
            <span className="text-xs text-text-muted mono">{adoptedCount}/{totalFeatures}</span>
          </div>
          <div className="h-1 bg-bm-border rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-success rounded-full transition-all duration-500"
              style={{ width: `${(adoptedCount / totalFeatures) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function EmptyColumn({ stage }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-bg-elevated flex items-center justify-center text-2xl mb-3">
        {stage === 'lead' ? '🎯' : stage === 'onboarding' ? '📋' : stage === 'active' ? '✅' : '💤'}
      </div>
      <p className="text-sm text-text-muted">No {stage} customers</p>
      {stage === 'lead' && (
        <p className="text-xs text-text-muted mt-1">Run the demo to seed customers</p>
      )}
    </div>
  );
}

export default function PipelineView({ pipeline, isLoading }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {STAGE_ORDER.map(stage => (
          <div key={stage} className="card animate-pulse">
            <div className="h-4 bg-bm-border rounded w-24 mb-4" />
            <div className="space-y-3">
              {[1, 2].map(i => <div key={i} className="h-16 bg-bm-border rounded-lg" />)}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-4 gap-4">
      {STAGE_ORDER.map(stage => {
        const config = STAGE_CONFIG[stage];
        const data = pipeline?.[stage] || { count: 0, customers: [] };
        return (
          <div key={stage} className={`rounded-xl border ${config.color} flex flex-col overflow-hidden`}>
            {/* Header */}
            <div className={`${config.headerBg} px-4 py-3 flex items-center justify-between border-b ${config.color}`}>
              <span className="text-sm font-semibold text-text-primary">{config.label}</span>
              <span className="text-xs mono bg-bg-elevated border border-bm-border text-text-secondary px-2 py-0.5 rounded-full">
                {data.count}
              </span>
            </div>
            {/* Cards */}
            <div className="flex-1 p-3 space-y-2 overflow-y-auto max-h-96">
              {data.customers.length === 0 ? (
                <EmptyColumn stage={stage} />
              ) : (
                data.customers.map(c => <CustomerCard key={c.id} customer={c} />)
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
