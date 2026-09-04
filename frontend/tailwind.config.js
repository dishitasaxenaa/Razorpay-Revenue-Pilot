/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        razorpay: {
          blue: "#0c2340",
          sky: "#0c83fd",
          hover: "#0266d6",
          dark: "#0b1426",
          light: "#f4f8fc"
        }
      }
    },
  },
  plugins: [],
}
