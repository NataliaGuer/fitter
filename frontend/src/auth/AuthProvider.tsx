import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import * as authApi from '../api/auth'
import { ApiError } from '../api/client'
import { AuthContext, type AuthContextValue, type AuthState } from './context'

async function checkSession(): Promise<AuthState> {
  try {
    const user = await authApi.me()
    return { status: 'authenticated', user }
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return { status: 'anonymous' }
    }
    // Network error, 5xx from the proxy, anything unexpected: keep the user "logged in", just offline.
    return { status: 'offline' }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    void checkSession().then((result) => {
      if (!cancelled) setState(result)
    })
    return () => {
      cancelled = true
    }
  }, [attempt])

  const retry = useCallback(() => {
    setState({ status: 'loading' })
    setAttempt((value) => value + 1)
  }, [])

  const login = useCallback(async (credentials: authApi.Credentials) => {
    const user = await authApi.login(credentials)
    setState({ status: 'authenticated', user })
  }, [])

  const register = useCallback(async (credentials: authApi.Credentials) => {
    const user = await authApi.register(credentials)
    setState({ status: 'authenticated', user })
  }, [])

  const logout = useCallback(async () => {
    // If the request does not reach the server the session is still valid: let the error propagate.
    await authApi.logout()
    setState({ status: 'anonymous' })
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ state, login, register, logout, retry }),
    [state, login, register, logout, retry],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
