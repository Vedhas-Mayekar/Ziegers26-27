/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/**/*.py',
    './events/templates/**/*.html',
    './events/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        noir: {
          950: '#090807',
          900: '#11100E',
          800: '#1A1815',
          700: '#28241F',
          600: '#3D3730',
        },
        parchment: {
          100: '#FAF4E8',
          200: '#E6D5B8',
          300: '#CBB287',
          400: '#A88D5D',
        },
        stamp: {
          red: '#DC2626',
          darkred: '#8B0000',
          gold: '#D97706',
          brass: '#B45309',
        }
      },
      fontFamily: {
        typewriter: ['"Special Elite"', 'cursive'],
        cinzel: ['Cinzel', 'serif'],
        sans: ['Outfit', 'sans-serif'],
      },
      backgroundImage: {
        'grunge-pattern': "radial-gradient(circle, rgba(220,38,38,0.05) 0%, rgba(9,8,7,0.95) 100%)",
        'dossier': "linear-gradient(135deg, #1A1815 0%, #11100E 100%)"
      }
    }
  },
  // Classes referenced only from JavaScript-injected strings (e.g. case modal)
  safelist: [
    'list-disc',
    'pl-4',
    'px-6',
    'hover:underline',
    'border-noir-700/80',
    'sm:flex-row',
    'sm:w-auto',
  ],
  plugins: [],
}
