export type ScenarioLabel =
  | 'BULLISH_PULLBACK_SWEEP'
  | 'BEARISH_SUPPLY_REJECTION'
  | 'STAND_ASIDE'

export interface PivotLevels {
  P?: number | null
  R1?: number | null
  R2?: number | null
  R3?: number | null
  R4?: number | null
  S1?: number | null
  S2?: number | null
  S3?: number | null
  S4?: number | null
}

export interface PivotsResponse {
  symbol: string
  anchor: string
  standard: PivotLevels
  camarilla: PivotLevels
  fibonacci: PivotLevels
}

export interface VolumeProfile {
  POC: number
  VAH: number
  VAL: number
  LVN: number
}

export interface VolumeProfileResponse extends VolumeProfile {
  symbol: string
}

export interface EntropyResponse {
  symbol: string
  entropy_bits: number
  classification: string
  clearance: boolean
}

export interface EntryRange {
  low: number
  high: number
}

export interface EntropySnapshot {
  bits: number
  classification: string
  clearance: boolean
}

export interface ForecastResponse {
  symbol: string
  timestamp_wat: string
  scenario: ScenarioLabel
  entry_range: EntryRange | null
  tp: number | null
  sl: number | null
  volume_profile: VolumeProfile
  entropy: EntropySnapshot
  regime: string
  mp_signals_retained: number
  position_size_multiplier: number
}

export interface ScraperStatus {
  symbol: string
  ohlcv: string
  last_bar_age_seconds: number | null
  futures: string
  yield_scraper: string
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  scrapers: ScraperStatus[]
  pairs_monitored: number
}

export interface PairInfo {
  symbol: string
  asset_class: string
  ecn_venue: string
  cme_futures_proxy: string
  macro_anchor: string
}

export interface PairsListResponse {
  pairs: PairInfo[]
}

export interface OHLCVBar {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface BarsResponse {
  symbol: string
  interval: string
  bars: OHLCVBar[]
}

export interface GarchSnapshot {
  conditional_variance: number
  percentile: number
  regime: string
  position_size_multiplier: number
  block_breakout_entries: boolean
  circuit_breaker_active: boolean
}

export interface MPFilterSnapshot {
  signals_retained: number
  noise_ceiling: number
  max_lags: number
  gamma: number
}

export interface PivotWeightsSnapshot {
  standard: number
  camarilla: number
  fibonacci: number
  volume_profile: number
}

export interface AnalyticsResponse {
  symbol: string
  price: number
  change_pct: number
  atr: number
  atr_percentile: number
  atr_regime: string
  garch: GarchSnapshot
  mp_filter: MPFilterSnapshot
  pivot_weights: PivotWeightsSnapshot
}

export interface MacroResponse {
  symbol: string
  macro_anchor: string
  yields: Record<string, number>
  spread: number | null
  source: string
}

export interface FuturesResponse {
  symbol: string
  cme_proxy: string
  volume: number
  open_interest: number
  source: string
}

export interface CotPosition {
  currency: string
  net_long: number
  net_short: number
  net_position: number
  bias: string
  source: string
  as_of: string | null
}

export interface CotResponse {
  positions: CotPosition[]
  updated: string | null
}

export interface GanttEvent {
  time_wat: string
  end_wat?: string | null
  label: string
  action: string
  priority: string
  type: string
  tp?: number | null
  sl?: number | null
}

export interface GanttResponse {
  symbol: string
  scenario: string
  events: GanttEvent[]
  executable: boolean
}

export interface SessionInfo {
  name: string
  start: string
  end: string
  description: string
  priority: string
  active: boolean
}

export interface SessionResponse {
  timestamp_wat: string
  active_sessions: { name: string; description: string; priority: string }[]
  next_session: { name: string; start: string; description: string; priority: string }
  is_london_open: boolean
  is_ny_overlap: boolean
  is_ny_close: boolean
  all_sessions: SessionInfo[]
}

export interface PairOverviewRow {
  symbol: string
  asset_class: string
  price: number
  change_pct: number
  scenario: string
  regime: string
  garch_regime: string
  entropy_bits: number
  clearance: boolean
  position_size_multiplier: number
  mp_signals: number
  actionable: boolean
}

export interface DeskOverviewResponse {
  timestamp_wat: string
  pairs: PairOverviewRow[]
  actionable_count: number
  blocked_count: number
  circuit_breaker_count: number
}

export interface RiskDeskResponse {
  timestamp_wat: string
  total_pairs: number
  stand_aside: number
  bullish: number
  bearish: number
  entropy_blocked: number
  circuit_breakers: number
  avg_entropy: number
  avg_position_multiplier: number
  high_priority_sessions_active: boolean
  pairs_at_risk: string[]
}

export interface PairData {
  forecast: ForecastResponse | null
  pivots: PivotsResponse | null
  profile: VolumeProfileResponse | null
  entropy: EntropyResponse | null
  analytics: AnalyticsResponse | null
  bars: BarsResponse | null
  macro: MacroResponse | null
  futures: FuturesResponse | null
  gantt: GanttResponse | null
  loading: boolean
  error: string | null
}

export interface DeskData {
  overview: DeskOverviewResponse | null
  risk: RiskDeskResponse | null
  sessions: SessionResponse | null
  cot: CotResponse | null
  loading: boolean
  error: string | null
}
