import { apiFetch } from './client'

/** Contract: CORE-002-BE-01. */
export type User = {
  id: number
  nickname: string
}

export type Credentials = {
  nickname: string
  pin: string
}

/** 200 → user; 401 → no valid session. Renews the session cookie. */
export function me(): Promise<User> {
  return apiFetch<User>('/api/auth/me')
}

/** 200 → user + cookie; 401 → wrong nickname or PIN; 422 → invalid input. */
export function login(credentials: Credentials): Promise<User> {
  return apiFetch<User>('/api/auth/login', { method: 'POST', body: credentials })
}

/** 201 → user + cookie; 409 → nickname already used; 422 → invalid input. */
export function register(credentials: Credentials): Promise<User> {
  return apiFetch<User>('/api/auth/register', { method: 'POST', body: credentials })
}

/** 204, idempotent. */
export function logout(): Promise<void> {
  return apiFetch<void>('/api/auth/logout', { method: 'POST' })
}
