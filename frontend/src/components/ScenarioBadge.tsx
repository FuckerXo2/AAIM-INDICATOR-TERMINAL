import type { ScenarioLabel } from '../api/types'

const CONFIG: Record<string, { label: string; tone: 'bull' | 'bear' | 'neutral' }> = {
  BULLISH_PULLBACK_SWEEP: { label: 'Bullish Pullback Sweep', tone: 'bull' },
  BEARISH_SUPPLY_REJECTION: { label: 'Bearish Supply Rejection', tone: 'bear' },
  STAND_ASIDE: { label: 'Stand Aside', tone: 'neutral' },
}

export function ScenarioBadge({ scenario }: { scenario: ScenarioLabel | string }) {
  const { label, tone } = CONFIG[scenario] ?? { label: scenario.replace(/_/g, ' '), tone: 'neutral' as const }
  return <span className={`badge badge-${tone}`}>{label}</span>
}
