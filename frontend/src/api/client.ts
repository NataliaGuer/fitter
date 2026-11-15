/** The server answered with a non-2xx status. The UI decides what to show from `status` (D-013). */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** The request did not reach the server (offline, VPN down, server unreachable). */
export class NetworkError extends Error {
  constructor(cause?: unknown) {
    super('Network error', { cause })
    this.name = 'NetworkError'
  }
}

type RequestOptions = {
  method?: 'GET' | 'POST'
  body?: unknown
}

/**
 * Same-origin JSON request to the backend (`/api/...`). The session cookie is HttpOnly and is
 * sent by the browser automatically.
 */
export async function apiFetch<T>(path: string, { method = 'GET', body }: RequestOptions = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      method,
      credentials: 'same-origin',
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (error) {
    throw new NetworkError(error)
  }

  if (!response.ok) {
    throw new ApiError(response.status, response.statusText)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
