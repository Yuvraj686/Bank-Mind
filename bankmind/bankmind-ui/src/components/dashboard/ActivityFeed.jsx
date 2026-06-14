import { useState } from 'react';
import { AgentBadge, agentBorderColor, formatTime, ConfidenceBar } from '../ui/shared';

function FeedEntry({ entry }) {
  const [expanded, setExpanded] = useState(false);
  const borderClass = agentBorderColor(entry.agent_name);
  const isNew = entry._new;

  return (
    <div className={`
      border-l-2 ${borderClass} pl-3 pr-3 py-2.5
      bg-bg-elevated rounded-r-lg
      ${isNew ? 'animate-slide-in-new animate-highlight-fade' : ''}
      transition-all duration-200
    `}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-wrap min-w-0">
          <AgentBadge agent={entry.agent_name} />
          <span className="text-xs font-medium text-text-primary truncate">{entry.customer_name}</span>
          <span className="text-xs text-text-muted mono">·</span>
          <span className="text-xs text-text-muted mono">{entry.action?.replace(/_/g, ' ')}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-text-muted mono">{formatTime(entry.created_at)}</span>
          {entry.reasoning && (
            <button
              onClick={() => setExpanded(e => !e)}
              className="text-xs text-accent-primary hover:text-blue-400 transition-colors font-medium"
            >
              {expanded ? 'Close' : 'Why?'}
            </button>
          )}
        </div>
      </div>

      {entry.message_sent && (
        <p className="mt-1.5 text-xs text-text-secondary line-clamp-2">{entry.message_sent}</p>
      )}

      {entry.was_overridden && (
        <div className="mt-1 inline-flex items-center gap-1 text-xs text-accent-warning">
          <span>⚠</span> Overridden by {entry.override_by}
        </div>
      )}

      {/* Expand reasoning */}
      {expanded && entry.reasoning && (
        <div className="mt-2 pt-2 border-t border-bm-border animate-fade-in" style={{ animation: 'fadeIn 200ms ease' }}>
          <p className="text-xs text-text-muted mb-1.5 font-medium">Reasoning</p>
          <p className="text-xs text-text-secondary leading-relaxed">{entry.reasoning}</p>
          {entry.confidence != null && (
            <div className="mt-2">
              <p className="text-xs text-text-muted mb-1">Confidence</p>
              <ConfidenceBar confidence={entry.confidence} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ActivityFeed({ entries, isLoading }) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="h-14 bg-bg-elevated rounded-r-lg border-l-2 border-bm-border animate-pulse" />
        ))}
      </div>
    );
  }

  if (!entries?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="text-3xl mb-3">📡</div>
        <p className="text-sm text-text-muted">No activity yet</p>
        <p className="text-xs text-text-muted mt-1">Run the demo to see live agent activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 overflow-y-auto max-h-96">
      {entries.map((entry, i) => (
        <FeedEntry key={entry.id || i} entry={entry} />
      ))}
    </div>
  );
}
