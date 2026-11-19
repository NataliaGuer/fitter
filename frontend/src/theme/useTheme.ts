import { useCallback, useSyncExternalStore } from 'react'

import { applyTheme, currentTheme, saveTheme, type Theme } from './theme'

// The applied theme lives on <html> (set by the inline script of index.html, which also follows
// system changes while the user has not chosen): observe it instead of duplicating the state.
function subscribe(onChange: () => void): () => void {
  const observer = new MutationObserver(onChange)
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
  return () => observer.disconnect()
}

/** Current theme and a setter that applies it and remembers the choice on this device (D-015). */
export function useTheme(): { theme: Theme; setTheme: (theme: Theme) => void } {
  const theme = useSyncExternalStore(subscribe, currentTheme)
  const setTheme = useCallback((next: Theme) => {
    saveTheme(next)
    applyTheme(next)
  }, [])
  return { theme, setTheme }
}
