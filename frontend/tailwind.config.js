/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        'xs': '375px',   // 小手機
        'sm': '640px',   // 大手機
        'md': '768px',   // 平板（豎屏）
        'lg': '1024px',  // 平板（橫屏）/ 桌面
        'xl': '1280px',  // 大桌面
        '2xl': '1536px', // 超大桌面
      },
      colors: {
        primary: {
          DEFAULT: '#6366F1',
          light: '#818CF8',
          dark: '#4F46E5',
        },
        secondary: {
          DEFAULT: '#60A5FA',
          light: '#93C5FD',
          dark: '#3B82F6',
        },
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
    },
  },
  plugins: [],
}

