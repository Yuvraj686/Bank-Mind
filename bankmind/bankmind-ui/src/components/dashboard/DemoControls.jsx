import { useState, useEffect } from 'react';
import { demoApi } from '../../lib/api';
import { LoadingSpinner, ErrorBanner } from '../ui/shared';

const STEPS = [
  { key: 'acquisition', label: 'Acquisition', icon: '🎯', color: 'text-accent-primary' },
  { key: 'onboarding',  label: 'Onboarding',  icon: '📋', color: 'text-accent-warning' },
  { key: 'adoption',    label: 'Adoption',     icon: '🚀', color: 'text-accent-success' },
  { key: 'life_event',  label: 'Life-Event',   icon: '⚡', color: 'text-accent-purple' },
];

export default function DemoControls({ compact = false, demoState, onAction }) {
  const [loading, setLoading] = useState(null); // 'seed' | 'run' | 'reset'
  const [error, setError] = useState(null);
  const [state, setState] = useState(demoState || { status: 'idle', step: null, progress: 0 });

  useEffect(() => {
    if (demoState) setState(demoState);
  }, [demoState]);

  // Poll demo state while running
  useEffect(() => {
    if (state.status !== 'running') return;
    const interval = setInterval(async () => {
      try {
        const s = await demoApi.state();
        setState(s);
        if (s.status !== 'running') clearInterval(interval);
      } catch (_) {}
    }, 2000);
    return () => clearInterval(interval);
  }, [state.status]);

  const handleAction = async (action) => {
    setLoading(action);
    setError(null);
    try {
      if (action === 'seed')  await demoApi.seed();
      if (action === 'run')   await demoApi.run();
      if (action === 'reset') { await demoApi.reset(); setState({ status: 'idle', step: null, progress: 0 }); }
      onAction?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(null);
    }
  };

  const isRunning = state.status === 'running';
  const isComplete = state.status === 'complete';
  const progress = state.progress || 0;

  return (
    <div className={compact ? 'flex items-center gap-3 flex-wrap' : 'card space-y-4'}>
      {!compact && (
        <div>
          <h3 className="text-sm font-semibold text-text-primary">Demo Controls</h3>
          <p className="text-xs text-text-muted mt-0.5">Seed, run, or reset the full customer journey demo</p>
        </div>
      )}

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {/* Buttons */}
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => handleAction('seed')}
          disabled={!!loading || isRunning}
          className="btn-ghost text-xs disabled:opacity-40"
          id="btn-demo-seed"
        >
          {loading === 'seed' ? <LoadingSpinner size={14} /> : '🌱'}
          Seed Data
        </button>
        <button
          onClick={() => handleAction('run')}
          disabled={!!loading || isRunning}
          className="btn-primary text-xs disabled:opacity-40"
          id="btn-demo-run"
        >
          {loading === 'run' || isRunning ? <LoadingSpinner size={14} /> : '▶'}
          {isRunning ? 'Running...' : 'Run Demo'}
        </button>
        <button
          onClick={() => handleAction('reset')}
          disabled={!!loading || isRunning}
          className="btn-danger text-xs disabled:opacity-40"
          id="btn-demo-reset"
        >
          {loading === 'reset' ? <LoadingSpinner size={14} /> : '↺'}
          Reset
        </button>
      </div>

      {/* Progress tracker */}
      {(isRunning || isComplete) && (
        <div className={compact ? 'flex items-center gap-3' : 'space-y-2'}>
          {!compact && (
            <div className="w-full bg-bm-border rounded-full h-1.5 overflow-hidden">
              <div
                className="h-full bg-accent-primary rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
          <div className="flex items-center gap-3 flex-wrap">
            {STEPS.map((step) => {
              const stepIndex = STEPS.findIndex(s => s.key === state.step);
              const myIndex = STEPS.findIndex(s => s.key === step.key);
              const done = isComplete || myIndex < stepIndex;
              const active = state.step === step.key;
              return (
                <div key={step.key} className="flex items-center gap-1.5">
                  <span className={`text-sm ${active ? 'animate-pulse' : ''}`}>
                    {done ? '✅' : active ? step.icon : '◌'}
                  </span>
                  <span className={`text-xs font-medium ${active ? step.color : done ? 'text-accent-success' : 'text-text-muted'}`}>
                    {step.label}
                  </span>
                  {myIndex < STEPS.length - 1 && <span className="text-text-muted text-xs">→</span>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Complete banner */}
      {isComplete && (
        <div className="flex items-center gap-2 bg-accent-success/10 border border-accent-success/30 text-accent-success rounded-lg px-4 py-2.5 text-sm font-medium">
          <span>✅</span>
          Demo complete — all 4 agents ran successfully!
        </div>
      )}
    </div>
  );
}
