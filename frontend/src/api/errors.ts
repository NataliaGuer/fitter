import { ApiError, NetworkError } from './client'

/**
 * Italian message for a failed request, chosen from the HTTP status (D-013).
 * `overrides` lets a screen give a status its own meaning (e.g. 401 on login).
 */
export function errorMessage(error: unknown, overrides: Partial<Record<number, string>> = {}): string {
  if (error instanceof NetworkError) {
    return 'Server non raggiungibile'
  }
  if (error instanceof ApiError) {
    const override = overrides[error.status]
    if (override !== undefined) return override
    if (error.status === 422) return 'Dati non validi'
    if (error.status >= 500) return 'Server non raggiungibile'
  }
  return 'Si è verificato un errore, riprova'
}
