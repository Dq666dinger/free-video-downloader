import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        cloud: '#f8fafc',
        accent: '#1777ff',
        accentSoft: '#dbeafe',
        dusk: '#101d40',
        rosefire: '#f43f5e'
      },
      boxShadow: {
        panel: '0 24px 80px rgba(15, 23, 42, 0.12)',
        glow: '0 20px 60px rgba(23, 119, 255, 0.20)'
      },
      backgroundImage: {
        halo: 'radial-gradient(circle at top left, rgba(23, 119, 255, 0.20), transparent 35%), radial-gradient(circle at bottom right, rgba(244, 63, 94, 0.14), transparent 30%)'
      },
      fontFamily: {
        display: ['"Space Grotesk"', '"Segoe UI"', 'sans-serif'],
        body: ['"Manrope"', '"Segoe UI"', 'sans-serif']
      }
    }
  },
  plugins: []
} satisfies Config;

