import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { PairData } from '../api/types'

const empty: PairData = {
  forecast: null,
  pivots: null,
  profile: null,
  entropy: null,
  analytics: null,
  bars: null,
  macro: null,
  futures: null,
  gantt: null,
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

export function usePairData(symbol: string) {
  const [data, setData] = useState<PairData>(empty)

  const refresh = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const [forecast, pivots, profile, entropy, analytics, bars, macro, futures, gantt] =
        await Promise.all([
          api.forecast(symbol),
          api.pivots(symbol),
          api.profile(symbol),
          api.entropy(symbol),
          safe(() => api.analytics(symbol)),
          safe(() => api.bars(symbol)),
          safe(() => api.macro(symbol)),
          safe(() => api.futures(symbol)),
          safe(() => api.gantt(symbol)),
        ])

      setData({
        forecast,
        pivots,
        profile,
        entropy,
        analytics,
        bars,
        macro,
        futures,
        gantt,
        loading: false,
        error: null,
      })
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to load pair data — is the backend running on port 8000?',
      }))
    }
  }, [symbol])

  useEffect(() => {
    refresh()
  }, [refresh])

  const updateForecast = useCallback((forecast: PairData['forecast']) => {
    setData((prev) => ({ ...prev, forecast }))
  }, [])

  return { data, refresh, updateForecast }
}
