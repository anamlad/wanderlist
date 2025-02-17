/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        "custom-blue": "#99c9db",
      },
      animation: {
        bounce: 'bounce 1s infinite',
      },
    },
    plugins: [],
  }
};
