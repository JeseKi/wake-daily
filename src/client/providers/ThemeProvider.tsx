import {
  type ReactNode,
  useEffect,
  useMemo,
  useState,
} from 'react'
import {
  ThemeContext,
  type ResolvedTheme,
  type ThemePreference,
} from '../contexts/ThemeContext'

const STORAGE_KEY = 'wake-daily-theme'
const THEME_VERSION_KEY = 'wake-daily-theme-version'
const THEME_VERSION = '2'
const DARK_MEDIA_QUERY = '(prefers-color-scheme: dark)'

function resolveSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') {
    return 'light'
  }

  return window.matchMedia(DARK_MEDIA_QUERY).matches ? 'dark' : 'light'
}

function resolveStoredPreference(): ThemePreference {
  if (typeof window === 'undefined') {
    return 'system'
  }

  if (window.localStorage.getItem(THEME_VERSION_KEY) !== THEME_VERSION) {
    window.localStorage.setItem(THEME_VERSION_KEY, THEME_VERSION)
    window.localStorage.setItem(STORAGE_KEY, 'light')
    return 'light'
  }

  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark' || stored === 'system') {
    return stored
  }

  return 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preference, setPreference] = useState<ThemePreference>(resolveStoredPreference)
  const [systemTheme, setSystemTheme] = useState<ResolvedTheme>(resolveSystemTheme)

  useEffect(() => {
    const mediaQuery = window.matchMedia(DARK_MEDIA_QUERY)
    const handleChange = (event: MediaQueryListEvent) => {
      setSystemTheme(event.matches ? 'dark' : 'light')
    }

    setSystemTheme(mediaQuery.matches ? 'dark' : 'light')
    mediaQuery.addEventListener('change', handleChange)

    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, preference)
  }, [preference])

  const resolvedTheme = preference === 'system' ? systemTheme : preference

  useEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme
    document.documentElement.style.colorScheme = resolvedTheme
  }, [resolvedTheme])

  const value = useMemo(
    () => ({
      preference,
      resolvedTheme,
      setPreference,
    }),
    [preference, resolvedTheme],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
