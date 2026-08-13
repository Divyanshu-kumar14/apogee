/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'apogee-blue': '#1e40af',
        'apogee-purple': '#7c3aed',
      }
    },
  },
  plugins: [],
}
