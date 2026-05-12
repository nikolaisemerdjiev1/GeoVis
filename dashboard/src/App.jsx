import Section from './components/Section'
import SimpleTable from './components/SimpleTable'
import { useDashboardData } from './hooks/useDashboardData'

function formatNumber(value, digits = 0) {
  if (value === null || value === undefined) return '—'
  return Number(value).toFixed(digits)
}

export default function App() {
  const { loading, error, health, recentGames, countryPerformance, confusionMatrix, practicePriorities } = useDashboardData()

  return (
    <main className="app-shell">
      <header className="hero card">
        <div>
          <p className="eyebrow">GeoVIS</p>
          <h1>Personal GeoGuessr analytics dashboard</h1>
          <p className="muted">
            Post-game only. Track countries, study confusions, and prioritize practice.
          </p>
        </div>
        <div className="status-pill">
          API: {loading ? 'Loading…' : error ? 'Unavailable' : health?.status ?? 'Unknown'}
        </div>
      </header>

      {error ? <p className="error card">Backend error: {error}</p> : null}

      <div className="grid two-up">
        <Section title="Recent games">
          <SimpleTable
            columns={[
              { key: 'played_at', label: 'Played At' },
              { key: 'map_name', label: 'Map' },
              { key: 'mode', label: 'Mode' },
              { key: 'total_score', label: 'Score' },
            ]}
            rows={recentGames}
          />
        </Section>

        <Section title="Practice priorities">
          <SimpleTable
            columns={[
              { key: 'country', label: 'Country' },
              { key: 'priority_score', label: 'Priority', render: (value) => formatNumber(value, 3) },
              { key: 'rounds_played', label: 'Rounds' },
              { key: 'avg_score', label: 'Avg Score', render: (value) => formatNumber(value, 0) },
            ]}
            rows={practicePriorities}
          />
        </Section>
      </div>

      <Section title="Country performance">
        <SimpleTable
          columns={[
            { key: 'actual_country', label: 'Country' },
            { key: 'rounds_played', label: 'Rounds' },
            { key: 'avg_score', label: 'Avg Score', render: (value) => formatNumber(value, 0) },
            { key: 'median_distance_km', label: 'Median Dist (km)', render: (value) => formatNumber(value, 1) },
            { key: 'correct_country_rate', label: 'Correct Rate', render: (value) => value == null ? '—' : `${formatNumber(value * 100, 1)}%` },
          ]}
          rows={countryPerformance}
        />
      </Section>

      <Section title="Confusion matrix preview">
        <SimpleTable
          columns={[
            { key: 'actual_country', label: 'Actual' },
            { key: 'guessed_country', label: 'Guessed' },
            { key: 'count', label: 'Count' },
          ]}
          rows={confusionMatrix}
        />
      </Section>
    </main>
  )
}
