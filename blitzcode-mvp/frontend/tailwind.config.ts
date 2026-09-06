import type { Config } from "tailwindcss";

// BlitzCode design tokens — dark competitive interface
// Signature: the Blitz Countdown, a digital timer fused with a terminal aesthetic
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "#0A0D12",       // page background — graphite black, not pure black
        surface: "#12161F",    // cards, panels
        elevated: "#1A1F2B",   // raised elements, modals, editor chrome
        line: "#262C3A",       // borders / dividers
        muted: "#8891A3",      // secondary text
        ink: "#EAEDF3",        // primary text
        blitz: {
          DEFAULT: "#4CF2C0",  // signature cyan — speed, active state, accepted-adjacent accent
          dim: "#2E8A73",
        },
        ember: {
          DEFAULT: "#FF5C4D",  // critical timer / danger
          dim: "#8C3229",
        },
        amber: {
          DEFAULT: "#FFB84D",  // mid-timer warning
        },
        success: "#4ADE80",
        danger: "#F2495C",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "IBM Plex Mono", "ui-monospace", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 24px rgba(76, 242, 192, 0.25)",
        "glow-ember": "0 0 24px rgba(255, 92, 77, 0.3)",
      },
      backgroundImage: {
        "hero-grid":
          "linear-gradient(rgba(76,242,192,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(76,242,192,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "40px 40px",
      },
    },
  },
  plugins: [],
};
export default config;
