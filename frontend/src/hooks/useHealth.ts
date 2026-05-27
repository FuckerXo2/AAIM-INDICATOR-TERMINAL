import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { HealthResponse } from '../api/types'

export function useHealth(intervalMs = 15000) {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const data = await api.health()
      setHealth(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Health check failed')
    }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, intervalMs)
    return () => clearInterval(id)
  }, [refresh, intervalMs])

  return { health, error, refresh }
}
