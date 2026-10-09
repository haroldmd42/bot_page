/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0B0F19',
          800: '#111827',
          700: '#1F2937',
          600: '#374151'
        },
        brand: {
          yellow: '#FACC15',
          red: '#EF4444',
          blue: '#3B82F6',
          purple: '#8B5CF6',
          emerald: '#10B981'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
