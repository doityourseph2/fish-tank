/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--color-ink)",
        ink2: "var(--color-ink2)",
        ink3: "var(--color-ink3)",
        base: "var(--color-base)",
        surface: "var(--color-surface)",
        surface2: "var(--color-surface2)",
        rule: "var(--color-rule)",
        rule2: "var(--color-rule2)",
        accent: "var(--color-accent)",
        success: "var(--color-success)",
        danger: "var(--color-danger)",
      },
      ringOffsetColor: {
        base: "var(--color-base)",
      },
      fontFamily: {
        sans: ["system-ui", "Segoe UI", "sans-serif"],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};
