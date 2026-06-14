// Shared UI component helpers

export function StageBadge({ stage }) {
  const map = {
    lead:       { cls: 'badge-lead',       label: 'Lead' },
    onboarding: { cls: 'badge-onboarding', label: 'Onboarding' },
    active:     { cls: 'badge-active',     label: 'Active' },
    dormant:    { cls: 'badge-dormant',    label: 'Dormant' },
  };
  const { cls, label } = map[stage] || { cls: 'badge-dormant', label: stage };
  return <span className={cls}><span className="w-1.5 h-1.5 rounded-full bg-current" />{label}</span>;
}

export function AgentBadge({ agent }) {
  const map = {
    acquisition: { cls: 'badge-acquisition',        label: '● Acquisition' },
    onboarding:  { cls: 'badge-onboarding-agent',   label: '● Onboarding' },
    adoption:    { cls: 'badge-adoption',            label: '● Adoption' },
    life_event:  { cls: 'badge-life_event',          label: '● Life-Event' },
    orchestrator:{ cls: 'bg-text-muted/10 text-text-muted inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium', label: '● Orchestrator' },
  };
  const { cls, label } = map[agent] || { cls: 'badge-dormant', label: agent };
  return <span className={cls}>{label}</span>;
}

export function ScoreRing({ score, size = 48 }) {
  const r = (size / 2) - 5;
  const circ = 2 * Math.PI * r;
  const pct = score == null ? 0 : Math.min(100, Math.max(0, score)) / 100;
  const dash = pct * circ;

  let color = '#EF4444'; // red
  if (score >= 90)      color = '#3B82F6'; // blue
  else if (score >= 70) color = '#10B981'; // green
  else if (score >= 50) color = '#F59E0B'; // amber

  return (
    <svg width={size} height={size} className="rotate-[-90deg]">
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#2D3748" strokeWidth={4} />
      <circle
        cx={size/2} cy={size/2} r={r}
        fill="none"
        stroke={color}
        strokeWidth={4}
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
      />
      <text
        x="50%" y="50%"
        dominantBaseline="central" textAnchor="middle"
        fill={color} fontSize={size < 40 ? 9 : 11}
        fontWeight="600" fontFamily="Inter"
        style={{ transform: `rotate(90deg) translateX(${size/2}px) translateY(-${size/2}px)` }}
      >
        {score == null ? '—' : Math.round(score)}
      </text>
    </svg>
  );
}

export function ConfidenceBar({ confidence }) {
  const pct = confidence == null ? 0 : Math.round(confidence * 100);
  const blocks = Math.round(pct / 20); // 0-5 filled blocks
  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-0.5">
        {Array.from({ length: 5 }, (_, i) => (
          <div
            key={i}
            className={`w-4 h-1.5 rounded-sm ${i < blocks ? 'bg-accent-primary' : 'bg-bm-border'}`}
          />
        ))}
      </div>
      <span className="text-xs text-text-muted mono">{pct}%</span>
    </div>
  );
}

export function AvatarInitials({ name, stage, size = 40 }) {
  const initials = name?.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || '??';
  const stageColors = {
    lead:       'bg-accent-primary/20 text-accent-primary',
    onboarding: 'bg-accent-warning/20 text-accent-warning',
    active:     'bg-accent-success/20 text-accent-success',
    dormant:    'bg-text-muted/20 text-text-muted',
  };
  const colorClass = stageColors[stage] || 'bg-accent-primary/20 text-accent-primary';
  return (
    <div
      className={`rounded-full flex items-center justify-center font-bold text-sm ${colorClass}`}
      style={{ width: size, height: size, flexShrink: 0 }}
    >
      {initials}
    </div>
  );
}

export function LoadingSpinner({ size = 20 }) {
  return (
    <svg
      className="animate-spin text-accent-primary"
      width={size} height={size}
      viewBox="0 0 24 24" fill="none"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="flex items-center justify-between bg-accent-danger/10 border border-accent-danger/30 text-accent-danger rounded-lg px-4 py-3 text-sm">
      <span>⚠ {message}</span>
      {onDismiss && <button onClick={onDismiss} className="ml-4 hover:opacity-70">✕</button>}
    </div>
  );
}

export function agentBorderColor(agent) {
  const map = {
    acquisition: 'border-accent-primary',
    onboarding:  'border-accent-warning',
    adoption:    'border-accent-success',
    life_event:  'border-accent-purple',
    orchestrator:'border-text-muted',
  };
  return map[agent] || 'border-bm-border';
}

export function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

export function formatDateTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}
