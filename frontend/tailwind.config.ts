import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        display: ['var(--font-cinzel)', 'serif'],
      },
      colors: {
        brand: {
           black: '#050505',
           gold: '#6e683b',
           blue: '#00f0ff',
        }
      },
      animation: {
        'fade-in': 'fadeIn 1s ease-out forwards',
        'shine': 'shine 3s infinite',
        'scroll': 'scroll 60s linear infinite',
      },
      keyframes: {
        scroll: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        shine: {
          '0%': { left: '-100%' },
          '100%': { left: '100%' },
        }
      }
    },
  },
  plugins: [],
};
export default config;
