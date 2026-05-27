import type {
  AnalyticsResponse,
  BarsResponse,
  CotResponse,
  DeskOverviewResponse,
  EntropyResponse,
  ForecastResponse,
  FuturesResponse,
  GanttResponse,
  HealthResponse,
  MacroResponse,
  PairsListResponse,
  PivotsResponse,
  RiskDeskResponse,
  SessionResponse,
  VolumeProfileResponse,
} from './types'

const BASE = import.meta.env.VITE_API_URL ?? '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  health: () => get<HealthResponse>('/health'),
  pairs: () => get<PairsListResponse>('/pairs'),

  deskOverview: () => get<DeskOverviewResponse>('/desk/overview'),
  deskRisk: () => get<RiskDeskResponse>('/desk/risk'),
  deskSessions: () => get<SessionResponse>('/desk/sessions'),
  deskCot: () => get<CotResponse>('/desk/cot'),

  forecast: (symbol: string) => get<ForecastResponse>(`/pairs/${symbol}/forecast`),
  pivots: (symbol: string) => get<PivotsResponse>(`/pairs/${symbol}/pivots`),
  profile: (symbol: string) => get<VolumeProfileResponse>(`/pairs/${symbol}/profile`),
  entropy: (symbol: string) => get<EntropyResponse>(`/pairs/${symbol}/entropy`),
  analytics: (symbol: string) => get<AnalyticsResponse>(`/pairs/${symbol}/analytics`),
  bars: (symbol: string, limit = 60) => get<BarsResponse>(`/pairs/${symbol}/bars?limit=${limit}`),
  macro: (symbol: string) => get<MacroResponse>(`/pairs/${symbol}/macro`),
  futures: (symbol: string) => get<FuturesResponse>(`/pairs/${symbol}/futures`),
  gantt: (symbol: string) => get<GanttResponse>(`/pairs/${symbol}/gantt`),
}

export function wsUrl(symbol: string): string {
  if (import.meta.env.VITE_API_URL) {
    const base = import.meta.env.VITE_API_URL.replace(/^http/, 'ws')
    return `${base}/ws/live/${symbol}`
  }
  if (import.meta.env.VITE_WS_URL) {
    return `${import.meta.env.VITE_WS_URL}/ws/live/${symbol}`
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/live/${symbol}`
}
