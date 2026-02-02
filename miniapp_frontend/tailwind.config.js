/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Telegram theme colors
        'tg-bg': 'var(--tg-theme-bg-color, #ffffff)',
        'tg-text': 'var(--tg-theme-text-color, #000000)',
        'tg-hint': 'var(--tg-theme-hint-color, #999999)',
        'tg-link': 'var(--tg-theme-link-color, #2481cc)',
        'tg-button': 'var(--tg-theme-button-color, #2481cc)',
        'tg-button-text': 'var(--tg-theme-button-text-color, #ffffff)',
        'tg-secondary-bg': 'var(--tg-theme-secondary-bg-color, #f1f1f1)',
        'tg-header-bg': 'var(--tg-theme-header-bg-color, #ffffff)',
        'tg-accent': 'var(--tg-theme-accent-text-color, #2481cc)',
        'tg-section-bg': 'var(--tg-theme-section-bg-color, #ffffff)',
        'tg-section-header': 'var(--tg-theme-section-header-text-color, #999999)',
        'tg-subtitle': 'var(--tg-theme-subtitle-text-color, #999999)',
        'tg-destructive': 'var(--tg-theme-destructive-text-color, #ff3b30)',
        // Activity zone colors
        'zone-low': '#3b82f6',     // blue
        'zone-medium': '#eab308',   // yellow
        'zone-high': '#ef4444',     // red
        // Signal colors
        'growth': '#22c55e',        // green
        'fall': '#ef4444',          // red
        'long': '#22c55e',          // green
        'short': '#ef4444',         // red
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
