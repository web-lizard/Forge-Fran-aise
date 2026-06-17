const viteEnv = (import.meta as any).env ?? {}

export const apiBase = viteEnv.VITE_API_BASE ?? 'http://127.0.0.1:8797/api'

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(apiBase + path)

  if (!response.ok) {
    throw new Error('GET ' + path + ' failed: ' + response.status)
  }

  return response.json()
}

export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(apiBase + path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error('POST ' + path + ' failed: ' + response.status)
  }

  return response.json()
}

export async function apiPatch<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(apiBase + path, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error('PATCH ' + path + ' failed: ' + response.status)
  }

  return response.json()
}

export async function apiDelete<T>(path: string): Promise<T> {
  const response = await fetch(apiBase + path, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error('DELETE ' + path + ' failed: ' + response.status)
  }

  return response.json()
}

export function publicApiUrl(path: string): string {
  return apiBase.replace('/api', '') + path
}