/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brain-blue': '#00b4d8',
        'brain-cyan': '#90e0ef',
        'brain-dark': '#0a0a0a',
        'brain-gray': '#1a1a1a',
        'brain-light': '#f8f9fa'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00b4d8, 0 0 10px #00b4d8, 0 0 15px #00b4d8' },
          '100%': { boxShadow: '0 0 10px #00b4d8, 0 0 20px #00b4d8, 0 0 30px #00b4d8' },
        }
      }
    },
  },
  plugins: [],
} 