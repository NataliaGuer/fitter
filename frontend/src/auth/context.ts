import { createContext } from 'react'

import type { Credentials, User } from '../api/auth'

export type AuthState =
  | { status: 'loading' }
  | { status: 'authenticated'; user: User }
  | { status: 'anonymous' }
  /** Server not reachable: never treated as a logout (D-010). */
  | { status: 'offline' }

export type AuthContextValue = {
  state: AuthState
  /** Rejects with ApiError / NetworkError: the caller shows the error. */
  login: (credentials: Credentials) => Promise<void>
  register: (credentials: Credentials) => Promise<void>
  logout: () => Promise<void>
  /** Checks the session again (used by the offline screen). */
  retry: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
