/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // BankMind design tokens
        'bg-base':      '#0D1117',
        'bg-surface':   '#161B22',
        'bg-elevated':  '#1C2230',
        'bm-border':    '#2D3748',
        'accent-primary':  '#3B82F6',
        'accent-success':  '#10B981',
        'accent-warning':  '#F59E0B',
        'accent-danger':   '#EF4444',
        'accent-purple':   '#8B5CF6',
        'text-primary':  '#F8FAFC',
        'text-secondary': '#94A3B8',
        'text-muted':    '#475569',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'slide-in': 'slideIn 300ms ease-out',
        'pulse-slow': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'count-up': 'countUp 800ms ease-out',
        'fade-in': 'fadeIn 200ms ease',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        countUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
