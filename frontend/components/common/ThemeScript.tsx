// components/common/ThemeScript.tsx

// This script is injected into the page to prevent theme flashing.
// It runs before React hydrates, so it directly manipulates the DOM.
const getThemeScript = () => {
  return `
    (function() {
      try {
        const theme = localStorage.getItem('app-store');
        if (theme) {
          const themeState = JSON.parse(theme).state.theme;
          const root = document.documentElement;
          
          // Remove any existing theme classes
          root.classList.remove('light', 'dark');
          
          if (themeState === 'dark' || (themeState === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            root.classList.add('dark');
          } else {
            root.classList.add('light');
          }
        }
      } catch (e) {
        // Fallback to system preference if localStorage parsing fails
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.add('light');
        }
      }
    })()
  `;
};

export function ThemeScript() {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: getThemeScript(),
      }}
      suppressHydrationWarning
    />
  );
}