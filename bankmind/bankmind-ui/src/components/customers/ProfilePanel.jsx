import { StageBadge, ScoreRing, AvatarInitials } from '../ui/shared';

const FEATURE_LABELS = {
  upi:         { label: 'UPI Payments',  icon: '💳' },
  sip:         { label: 'SIP / Mutual Fund', icon: '📈' },
  fd:          { label: 'Fixed Deposit', icon: '🏦' },
  credit_card: { label: 'Credit Card',   icon: '💳' },
  home_loan:   { label: 'Home Loan',     icon: '🏠' },
};

export default function ProfilePanel({ customer }) {
  if (!customer) return (
    <div className="flex items-center justify-center h-40 text-text-muted text-sm">No customer selected</div>
  );

  const features = customer.features_adopted || {};
  const adoptedCount = Object.values(features).filter(Boolean).length;

  return (
    <div className="space-y-4">
      {/* Avatar + name + stage */}
      <div className="flex items-center gap-4">
        <AvatarInitials name={customer.name} stage={customer.stage} size={52} />
        <div className="min-w-0">
          <h2 className="text-base font-bold text-text-primary truncate">{customer.name}</h2>
          <p className="text-xs text-text-muted">{customer.occupation} · {customer.city}</p>
          <div className="mt-1.5">
            <StageBadge stage={customer.stage} />
          </div>
        </div>
      </div>

      {/* Score ring */}
      {customer.lead_score != null && (
        <div className="flex items-center gap-4 card-elevated">
          <ScoreRing score={customer.lead_score} size={56} />
          <div>
            <p className="text-xs text-text-muted">Lead Score</p>
            <p className="text-2xl font-bold text-text-primary mono">{Math.round(customer.lead_score)}</p>
            <p className="text-xs text-text-muted">/ 100</p>
          </div>
        </div>
      )}

      {/* KYC info */}
      {customer.account_number && (
        <div className="card-elevated">
          <p className="text-xs text-text-muted mb-1">Account Number</p>
          <p className="mono text-accent-primary text-sm font-medium">{customer.account_number}</p>
          <p className="text-xs text-text-muted mt-1">KYC: <span className={customer.kyc_status === 'verified' ? 'text-accent-success' : 'text-accent-danger'}>{customer.kyc_status}</span></p>
        </div>
      )}

      {/* Profile details */}
      <div className="card-elevated space-y-2 text-xs">
        <div className="flex justify-between">
          <span className="text-text-muted">Age</span>
          <span className="text-text-primary font-medium">{customer.age}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Income</span>
          <span className="text-text-primary font-medium">₹{(customer.income_monthly || 0).toLocaleString('en-IN')}/mo</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Web Visits</span>
          <span className="text-text-primary font-medium">{customer.website_visits || 0}</span>
        </div>
        {customer.last_life_event_detected && (
          <div className="flex justify-between">
            <span className="text-text-muted">Life Event</span>
            <span className="text-accent-purple font-medium">{customer.last_life_event_detected.replace(/_/g, ' ')}</span>
          </div>
        )}
      </div>

      {/* Features adopted */}
      {customer.stage === 'active' && (
        <div className="card-elevated">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-semibold text-text-primary">Features</p>
            <span className="mono text-xs text-text-muted">{adoptedCount}/{Object.keys(features).length}</span>
          </div>
          <div className="space-y-2">
            {Object.entries(features).map(([key, adopted]) => {
              const feat = FEATURE_LABELS[key] || { label: key, icon: '●' };
              return (
                <div key={key} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{feat.icon}</span>
                    <span className="text-xs text-text-secondary">{feat.label}</span>
                  </div>
                  <span className={`text-xs font-medium ${adopted ? 'text-accent-success' : 'text-text-muted'}`}>
                    {adopted ? '✓ Active' : '○ Unused'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
