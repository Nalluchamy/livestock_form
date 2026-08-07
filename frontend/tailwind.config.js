/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        civic: {
          navy: "#0F172A",
          slate: "#1E293B",
          teal: "#0D9488",
          lightTeal: "#14B8A6",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#EF4444",
          bg: "#F8FAFC",
          card: "#FFFFFF",
        }
      }
    },
  },
  plugins: [],
}
