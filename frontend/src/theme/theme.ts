// Theme choice (D-015). The same logic runs, before the bundle, in the inline script of index.html:
// keep the two in sync (storage key, classes, theme-color values).

export type Theme = 'light' | 'dark'

export const THEME_STORAGE_KEY = 'fitter-theme'

const THEME_COLORS: Record<Theme, string> = { light: '#FAFADF', dark: '#111111' }

/** The theme chosen by the user on this device, or null to follow the system. */
export function storedTheme(): Theme | null {
  try {
    const value = localStorage.getItem(THEME_STORAGE_KEY)
    return value === 'light' || value === 'dark' ? value : null
  } catch {
    return null // storage unavailable (e.g. private browsing): follow the system
  }
}

export function saveTheme(theme: Theme): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {
    // storage unavailable: the choice lasts until the page is reloaded
  }
}

export function systemTheme(): Theme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/** The theme currently applied to <html>. */
export function currentTheme(): Theme {
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'
}

/** Applies a theme to <html> (HeroUI classes, color-scheme, browser bar color). */
export function applyTheme(theme: Theme): void {
  const root = document.documentElement
  root.classList.toggle('dark', theme === 'dark')
  root.classList.toggle('light', theme === 'light')
  root.dataset.theme = theme
  root.style.colorScheme = theme
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', THEME_COLORS[theme])
}
