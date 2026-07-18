/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f4f8',
          100: '#d9e1ec',
          500: '#1a365d',
          600: '#153e75',
          700: '#0f2847',
        },
        'amber-analytics': '#f59e0b',
        'geo-purple': '#9333ea',
        'viz-blue': '#3b82f6',
        'alert-red': '#ef4444',
        'gov-slate': '#64748b',
        'data-green': '#10b981',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        kpi: ['Inter', 'system-ui', 'sans-serif'],
        table: ['Inter', 'system-ui', 'sans-serif'],
        map: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        kpi: ['2rem', { lineHeight: '2.25rem', fontWeight: '700' }],
        'table-sm': ['0.8125rem', { lineHeight: '1.25rem' }],
        'map-label': ['0.6875rem', { lineHeight: '1rem' }],
      },
    },
  },
  plugins: [],
};
