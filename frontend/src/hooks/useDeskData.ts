import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { DeskData } from '../api/types'

const empty: DeskData = {
  overview: null,
  risk: null,
  sessions: null,
  cot: null,
  loading: true,
  error: null,
}

async function safe<T>(fn: () => Promise<T>): Promise<T | null> {
  try {
    return await fn()
  } catch {
    return null
  }
}

export function useDeskData(intervalMs = 30000) {
  const [data, setData] = useState<DeskData>(empty)

  const refresh = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true }))
    try {
      const [overview, risk, sessions, cot] = await Promise.all([
        safe(() => api.deskOverview()),
        safe(() => api.deskRisk()),
        safe(() => api.deskSessions()),
        safe(() => api.deskCot()),
      ])

      const allFailed = !overview && !risk && !sessions && !cot
      setData({
        overview,
        risk,
        sessions,
        cot,
        loading: false,
        error: allFailed
          ? 'Desk endpoints unavailable — restart the backend (uvicorn aaim_terminal.main:app --reload)'
          : null,
      })
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to load desk data',
      }))
    }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, intervalMs)
    return () => clearInterval(id)
  }, [refresh, intervalMs])

  return { data, refresh }
}
