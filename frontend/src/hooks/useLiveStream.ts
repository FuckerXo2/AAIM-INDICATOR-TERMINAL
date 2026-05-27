import { useEffect, useRef, useState } from 'react'
import { wsUrl } from '../api/client'
import type { ForecastResponse } from '../api/types'

export function useLiveStream(
  symbol: string,
  enabled: boolean,
  onForecast: (forecast: ForecastResponse) => void,
) {
  const [connected, setConnected] = useState(false)
  const onForecastRef = useRef(onForecast)
  onForecastRef.current = onForecast

  useEffect(() => {
    if (!enabled) {
      setConnected(false)
      return
    }

    let ws: WebSocket | null = null
    let retryTimer: ReturnType<typeof setTimeout> | null = null
    let closed = false

    const connect = () => {
      if (closed) return
      ws = new WebSocket(wsUrl(symbol))

      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        if (!closed) retryTimer = setTimeout(connect, 5000)
      }
      ws.onerror = () => ws?.close()
      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data as string)
          if (payload.forecast) onForecastRef.current(payload.forecast)
        } catch {
          /* ignore malformed frames */
        }
      }
    }

    connect()

    return () => {
      closed = true
      if (retryTimer) clearTimeout(retryTimer)
      ws?.close()
      setConnected(false)
    }
  }, [symbol, enabled])

  return { connected }
}
