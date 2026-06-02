/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#050810',
        foreground: '#e0e6f0',
        card: {
          DEFAULT: '#0a0f1a',
          foreground: '#e0e6f0',
        },
        primary: {
          DEFAULT: '#00f0ff',
          foreground: '#050810',
        },
        secondary: {
          DEFAULT: '#0d1320',
          foreground: '#7a8ba8',
        },
        muted: {
          DEFAULT: '#111827',
          foreground: '#4a5568',
        },
        accent: {
          DEFAULT: '#ff9500',
          foreground: '#050810',
        },
        destructive: {
          DEFAULT: '#ff3366',
          foreground: '#ffffff',
        },
        border: '#151d2e',
        input: '#1e293b',
        ring: '#00f0ff',
        'severity-low': '#00ff88',
        'severity-medium': '#ff9500',
        'severity-high': '#ff6633',
        'severity-critical': '#ff3366',
        'llm-accent': '#b366ff',
        'surface': '#0a0f1a',
        'surface-raised': '#0d1320',
        'surface-overlay': '#111827',
        'border-bright': '#1e293b',
        'border-glow': '#00f0ff',
        'cyan': '#00f0ff',
        'cyan-dim': '#0099aa',
        'amber': '#ff9500',
        'amber-dim': '#cc7700',
        'red': '#ff3366',
        'green': '#00ff88',
        'green-dim': '#00cc6a',
        'purple': '#b366ff',
        'text': '#e0e6f0',
        'text-secondary': '#7a8ba8',
        'text-dim': '#708096',
        'void': '#050810',
      },
      fontFamily: {
        sans: ['Outfit', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'monospace'],
      },
      borderRadius: {
        lg: '12px',
        md: '8px',
        sm: '4px',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'slide-up': 'slide-up 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        'shimmer': 'shimmer 2s linear infinite',
      },
    },
  },
  plugins: [],
}
