import { useEffect, useRef, useState } from 'react';
import { LoadingSpinner } from '../ui/shared';

export default function KPITile({ label, value, delta, prefix = '', suffix = '', color = 'text-accent-primary', isLoading }) {
  const [displayValue, setDisplayValue] = useState(0);
  const [animated, setAnimated] = useState(false);
  const prevRef = useRef(null);

  // Count-up animation on value change
  useEffect(() => {
    if (value == null || isLoading) return;
    const target = typeof value === 'number' ? value : parseFloat(value) || 0;
    const start = prevRef.current ?? 0;
    prevRef.current = target;

    if (start === target) {
      setDisplayValue(target);
      return;
    }

    setAnimated(true);
    const duration = 800;
    const startTime = performance.now();

    const tick = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setDisplayValue(Math.round(start + (target - start) * eased));
      if (progress < 1) requestAnimationFrame(tick);
      else {
        setDisplayValue(target);
        setTimeout(() => setAnimated(false), 200);
      }
    };
    requestAnimationFrame(tick);
  }, [value, isLoading]);

  const formatted = typeof displayValue === 'number'
    ? displayValue % 1 === 0
      ? displayValue.toLocaleString('en-IN')
      : displayValue.toFixed(1)
    : displayValue;

  return (
    <div className={`card flex flex-col gap-3 hover:border-bm-border/80 transition-colors ${animated ? 'animate-pulse-slow' : ''}`}>
      <p className="text-xs font-medium text-text-muted uppercase tracking-wider">{label}</p>
      {isLoading ? (
        <div className="h-9 flex items-center"><LoadingSpinner size={24} /></div>
      ) : (
        <div className="flex items-end justify-between">
          <p className={`text-3xl font-bold ${color} font-mono`} style={{ animation: animated ? 'countUp 800ms ease-out' : 'none' }}>
            {prefix}{formatted}{suffix}
          </p>
          {delta != null && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              delta > 0 ? 'bg-accent-success/10 text-accent-success' :
              delta < 0 ? 'bg-accent-danger/10 text-accent-danger' :
              'bg-text-muted/10 text-text-muted'
            }`}>
              {delta > 0 ? '+' : ''}{delta}%
            </span>
          )}
        </div>
      )}
    </div>
  );
}
