import { useState } from 'react';
import { AgentBadge, StageBadge, ConfidenceBar, formatDateTime } from '../ui/shared';
import { agentsApi } from '../../lib/api';

function LogEntry({ log, onOverride }) {
  const [expanded, setExpanded] = useState(false);
  const [overrideOpen, setOverrideOpen] = useState(false);

  return (
    <div className={`
      border border-bm-border rounded-lg overflow-hidden
      ${log.was_overridden ? 'border-l-2 border-l-accent-warning' : ''}
      hover:border-bm-border/80 transition-colors
    `}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 px-4 py-3 bg-bg-elevated">
        <div className="flex items-center gap-2 flex-wrap min-w-0">
          <AgentBadge agent={log.agent_name} />
          <span className="text-xs mono text-text-muted">{log.action?.replace(/_/g, ' ')}</span>
          {log.stage_before !== log.stage_after && log.stage_after && (
            <div className="flex items-center gap-1 text-xs">
              <StageBadge stage={log.stage_before} />
              <span className="text-text-muted">→</span>
              <StageBadge stage={log.stage_after} />
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs mono text-text-muted">{formatDateTime(log.created_at)}</span>
          <button
            onClick={() => setExpanded(e => !e)}
            className="text-xs text-accent-primary hover:text-blue-400 transition-colors"
          >
            {expanded ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {/* Message preview */}
      {log.message_sent && (
        <div className="px-4 py-2 border-t border-bm-border">
          <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed">{log.message_sent}</p>
        </div>
      )}

      {/* Override badge */}
      {log.was_overridden && (
        <div className="px-4 py-1.5 bg-accent-warning/5 border-t border-accent-warning/20">
          <span className="text-xs text-accent-warning">⚠ Overridden by {log.override_by} — {log.override_note}</span>
        </div>
      )}

      {/* Expanded: reasoning + confidence + override button */}
      {expanded && (
        <div className="px-4 py-3 border-t border-bm-border space-y-3 animate-fade-in">
          {log.reasoning && (
            <div>
              <p className="text-xs font-medium text-text-muted mb-1">Reasoning</p>
              <p className="text-xs text-text-secondary leading-relaxed">{log.reasoning}</p>
            </div>
          )}
          {log.confidence != null && (
            <div>
              <p className="text-xs font-medium text-text-muted mb-1">Confidence</p>
              <ConfidenceBar confidence={log.confidence} />
            </div>
          )}
          {!log.was_overridden && (
            <button
              onClick={() => setOverrideOpen(true)}
              className="btn-warning text-xs"
            >
              ✏ Override
            </button>
          )}
        </div>
      )}

      {/* Override panel */}
      {overrideOpen && (
        <OverridePanel
          log={log}
          onClose={() => setOverrideOpen(false)}
          onSuccess={() => { setOverrideOpen(false); onOverride?.(); }}
        />
      )}
    </div>
  );
}

function OverridePanel({ log, onClose, onSuccess }) {
  const [action, setAction] = useState('cancel');
  const [note, setNote] = useState('');
  const [newMessage, setNewMessage] = useState(log.message_sent || '');
  const [newStage, setNewStage] = useState('active');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      await agentsApi.override(log.id, {
        action,
        note,
        new_message: action === 'edit_message' ? newMessage : undefined,
        new_stage: action === 'move_stage' ? newStage : undefined,
      });
      onSuccess();
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <div className="border-t border-bm-border bg-bg-surface/50 px-4 py-4 space-y-3">
      <p className="text-sm font-semibold text-text-primary">Override Action</p>

      {/* Action selection */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { key: 'cancel', label: '✕ Cancel Action', color: 'border-accent-danger text-accent-danger' },
          { key: 'edit_message', label: '✏ Edit Message', color: 'border-accent-warning text-accent-warning' },
          { key: 'move_stage', label: '→ Move Stage', color: 'border-accent-primary text-accent-primary' },
        ].map(opt => (
          <button
            key={opt.key}
            onClick={() => setAction(opt.key)}
            className={`text-xs px-3 py-2 rounded-lg border transition-colors ${
              action === opt.key ? opt.color + ' bg-opacity-10' : 'border-bm-border text-text-muted'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {action === 'edit_message' && (
        <textarea
          value={newMessage}
          onChange={e => setNewMessage(e.target.value)}
          className="input resize-none"
          rows={3}
          placeholder="Edit the message..."
        />
      )}

      {action === 'move_stage' && (
        <select
          value={newStage}
          onChange={e => setNewStage(e.target.value)}
          className="input"
        >
          {['lead', 'onboarding', 'active', 'dormant'].map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      )}

      <textarea
        value={note}
        onChange={e => setNote(e.target.value)}
        className="input resize-none"
        rows={2}
        placeholder="Reason for override (optional)..."
      />

      {error && <p className="text-xs text-accent-danger">{error}</p>}

      <div className="flex gap-2">
        <button onClick={handleSubmit} disabled={loading} className="btn-primary text-xs">
          {loading ? 'Saving...' : 'Confirm Override'}
        </button>
        <button onClick={onClose} className="btn-ghost text-xs">Cancel</button>
      </div>
    </div>
  );
}

export default function AgentLogPanel({ logs, isLoading, onOverride }) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map(i => <div key={i} className="h-20 bg-bg-elevated rounded-lg animate-pulse" />)}
      </div>
    );
  }

  if (!logs?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="text-3xl mb-3">📊</div>
        <p className="text-sm text-text-muted">No agent activity yet</p>
        <p className="text-xs text-text-muted mt-1">Run the demo or trigger an agent manually</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 overflow-y-auto">
      {logs.map((log) => (
        <LogEntry key={log.id} log={log} onOverride={onOverride} />
      ))}
    </div>
  );
}
