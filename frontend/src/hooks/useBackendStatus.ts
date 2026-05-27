import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'

export interface BackendStatus {
  connected: boolean
  version: string | null
  hasDeskRoutes: boolean
  error: string | null
}

export function useBackendStatus(pollMs = 10000) {
  const [status, setStatus] = useState<BackendStatus>({
    connected: false,
    version: null,
    hasDeskRoutes: false,
    error: null,
  })

  const check = useCallback(async () => {
    try {
      const [health, root] = await Promise.all([
        api.health(),
        fetch(`${import.meta.env.VITE_API_URL ?? '/api'}/`).then((r) => r.json()),
      ])
      const endpoints = (root as { endpoints?: Record<string, string> }).endpoints ?? {}
      setStatus({
        connected: true,
        version: (root as { version?: string }).version ?? null,
        hasDeskRoutes: 'desk_overview' in endpoints,
        error: health.status === 'degraded' ? 'Scrapers degraded' : null,
      })
    } catch (err) {
      setStatus({
        connected: false,
        version: null,
        hasDeskRoutes: false,
        error: err instanceof Error ? err.message : 'Backend unreachable',
      })
    }
  }, [])

  useEffect(() => {
    check()
    const id = setInterval(check, pollMs)
    return () => clearInterval(id)
  }, [check, pollMs])

  return { status, check }
}
