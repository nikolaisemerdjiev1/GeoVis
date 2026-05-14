import { useEffect, useMemo, useState } from 'react'
import { api } from './api/client'
import Section from './components/Section'
import SimpleTable from './components/SimpleTable'
import { useDashboardData } from './hooks/useDashboardData'

function formatNumber(value, digits = 0) {
  if (value === null || value === undefined) return '-'
  return Number(value).toFixed(digits)
}

const DEFAULT_MISTAKE_TYPES = [
  'country confusion',
  'region confusion',
  'landscape read',
  'road signs',
  'language/script',
  'urban/rural mismatch',
  'time management',
]

export default function App() {
  const {
    loading,
    error,
    health,
    recentGames,
    recentImports,
    roundReviews,
    reviewOptions,
    reviewQueue,
    countryPerformance,
    regionPerformance,
    confusionMatrix,
    regionConfusionMatrix,
    practicePriorities,
  } = useDashboardData()
  const [reviewRows, setReviewRows] = useState([])
  const [selectedRoundId, setSelectedRoundId] = useState(null)
  const [reviewFilters, setReviewFilters] = useState({ mistakeType: '', tag: '', reviewed: 'all' })
  const [reviewDraft, setReviewDraft] = useState({ mistake_type: '', manual_notes: '', tagsText: '' })
  const [reviewStatus, setReviewStatus] = useState(null)

  useEffect(() => {
    setReviewRows(roundReviews)
    if (!selectedRoundId && roundReviews.length > 0) {
      setSelectedRoundId(roundReviews[0].id)
    }
  }, [roundReviews, selectedRoundId])

  const filteredReviewRows = useMemo(() => {
    return reviewRows.filter((row) => {
      const mistakeMatch = reviewFilters.mistakeType
        ? (row.mistake_type ?? '').toLowerCase() === reviewFilters.mistakeType.toLowerCase()
        : true
      const tagMatch = reviewFilters.tag ? row.tags?.includes(reviewFilters.tag.toLowerCase()) : true
      const reviewedMatch =
        reviewFilters.reviewed === 'all'
          ? true
          : reviewFilters.reviewed === 'reviewed'
            ? row.reviewed
            : !row.reviewed
      return mistakeMatch && tagMatch && reviewedMatch
    })
  }, [reviewFilters, reviewRows])

  const selectedRound = useMemo(
    () => reviewRows.find((row) => row.id === selectedRoundId) ?? filteredReviewRows[0] ?? null,
    [filteredReviewRows, reviewRows, selectedRoundId],
  )

  useEffect(() => {
    if (!selectedRound) return
    setReviewDraft({
      mistake_type: selectedRound.mistake_type ?? '',
      manual_notes: selectedRound.manual_notes ?? '',
      tagsText: selectedRound.tags?.join(', ') ?? '',
    })
  }, [selectedRound])

  const mistakeTypeOptions = useMemo(() => {
    return Array.from(new Set([...DEFAULT_MISTAKE_TYPES, ...(reviewOptions.mistake_types ?? [])])).sort()
  }, [reviewOptions.mistake_types])

  const saveRoundReview = async () => {
    if (!selectedRound) return
    setReviewStatus('Saving review...')
    const payload = {
      mistake_type: reviewDraft.mistake_type,
      manual_notes: reviewDraft.manual_notes,
      tags: reviewDraft.tagsText
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
    }
    try {
      const updated = await api.updateRoundNote(selectedRound.id, payload)
      setReviewRows((rows) => rows.map((row) => (row.id === updated.id ? updated : row)))
      setSelectedRoundId(updated.id)
      setReviewStatus('Review saved.')
    } catch (saveError) {
      setReviewStatus(`Save failed: ${saveError.message}`)
    }
  }

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
          API: {loading ? 'Loading...' : error ? 'Unavailable' : health?.status ?? 'Unknown'}
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
              { key: 'target_type', label: 'Type' },
              { key: 'country', label: 'Target', render: (value, row) => [value, row.region].filter(Boolean).join(' / ') },
              { key: 'priority_score', label: 'Priority', render: (value) => formatNumber(value, 3) },
              { key: 'rounds_played', label: 'Rounds' },
              { key: 'avg_score', label: 'Avg Score', render: (value) => formatNumber(value, 0) },
              { key: 'explanation', label: 'Why' },
            ]}
            rows={practicePriorities}
          />
        </Section>
      </div>

      <Section title="Import history">
        <SimpleTable
          columns={[
            { key: 'created_at', label: 'Imported At' },
            { key: 'external_game_id', label: 'Game ID' },
            { key: 'status', label: 'Status' },
            { key: 'message', label: 'Message' },
          ]}
          rows={recentImports}
        />
      </Section>

      <Section title="Training workflow">
        <div className="grid three-up">
          <div>
            <h3>Recent misses</h3>
            <SimpleTable
              columns={[
                {
                  key: 'round_number',
                  label: 'Round',
                  render: (value, row) => (
                    <button className="link-button" type="button" onClick={() => setSelectedRoundId(row.id)}>
                      {row.map_name ?? 'Game'} R{value}
                    </button>
                  ),
                },
                { key: 'actual_country', label: 'Actual', render: (value, row) => [value, row.actual_region].filter(Boolean).join(' / ') },
                { key: 'guessed_country', label: 'Guessed', render: (value, row) => [value, row.guessed_region].filter(Boolean).join(' / ') },
                { key: 'score', label: 'Score' },
              ]}
              rows={reviewQueue.recent_misses}
            />
          </div>

          <div>
            <h3>Recurring confusions</h3>
            <SimpleTable
              columns={[
                {
                  key: 'round_number',
                  label: 'Round',
                  render: (value, row) => (
                    <button className="link-button" type="button" onClick={() => setSelectedRoundId(row.id)}>
                      {row.map_name ?? 'Game'} R{value}
                    </button>
                  ),
                },
                { key: 'actual_country', label: 'Actual', render: (value, row) => [value, row.actual_region].filter(Boolean).join(' / ') },
                { key: 'guessed_country', label: 'Guessed', render: (value, row) => [value, row.guessed_region].filter(Boolean).join(' / ') },
              ]}
              rows={reviewQueue.recurring_confusions}
            />
          </div>

          <div>
            <h3>Tagged rounds</h3>
            <SimpleTable
              columns={[
                {
                  key: 'round_number',
                  label: 'Round',
                  render: (value, row) => (
                    <button className="link-button" type="button" onClick={() => setSelectedRoundId(row.id)}>
                      {row.map_name ?? 'Game'} R{value}
                    </button>
                  ),
                },
                { key: 'mistake_type', label: 'Mistake', render: (value) => value ?? '-' },
                { key: 'tags', label: 'Tags', render: (value) => value?.join(', ') || '-' },
              ]}
              rows={reviewQueue.tagged_rounds}
            />
          </div>
        </div>
      </Section>

      <Section title="Round review">
        <div className="review-layout">
          <div>
            <div className="filter-row">
              <label>
                Mistake
                <select
                  value={reviewFilters.mistakeType}
                  onChange={(event) => setReviewFilters((filters) => ({ ...filters, mistakeType: event.target.value }))}
                >
                  <option value="">All mistakes</option>
                  {mistakeTypeOptions.map((mistakeType) => (
                    <option key={mistakeType} value={mistakeType}>{mistakeType}</option>
                  ))}
                </select>
              </label>
              <label>
                Tag
                <select
                  value={reviewFilters.tag}
                  onChange={(event) => setReviewFilters((filters) => ({ ...filters, tag: event.target.value }))}
                >
                  <option value="">All tags</option>
                  {(reviewOptions.tags ?? []).map((tag) => (
                    <option key={tag} value={tag}>{tag}</option>
                  ))}
                </select>
              </label>
              <label>
                Status
                <select
                  value={reviewFilters.reviewed}
                  onChange={(event) => setReviewFilters((filters) => ({ ...filters, reviewed: event.target.value }))}
                >
                  <option value="all">All rounds</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="unreviewed">Unreviewed</option>
                </select>
              </label>
            </div>

            <SimpleTable
              columns={[
                {
                  key: 'round_number',
                  label: 'Round',
                  render: (value, row) => (
                    <button className="link-button" type="button" onClick={() => setSelectedRoundId(row.id)}>
                      {row.map_name ?? 'Game'} R{value}
                    </button>
                  ),
                },
                { key: 'actual_country', label: 'Actual', render: (value, row) => [value, row.actual_region].filter(Boolean).join(' / ') },
                { key: 'guessed_country', label: 'Guessed', render: (value, row) => [value, row.guessed_region].filter(Boolean).join(' / ') },
                { key: 'score', label: 'Score' },
                { key: 'mistake_type', label: 'Mistake', render: (value) => value ?? '-' },
                { key: 'tags', label: 'Tags', render: (value) => value?.join(', ') || '-' },
              ]}
              rows={filteredReviewRows}
            />
          </div>

          <aside className="review-editor">
            {selectedRound ? (
              <>
                <div>
                  <p className="eyebrow">Selected round</p>
                  <h3>{selectedRound.map_name ?? 'Game'} - Round {selectedRound.round_number}</h3>
                  <p className="muted">
                    {[selectedRound.actual_country, selectedRound.actual_region].filter(Boolean).join(' / ')}
                    {' vs '}
                    {[selectedRound.guessed_country, selectedRound.guessed_region].filter(Boolean).join(' / ')}
                  </p>
                </div>

                <label>
                  Mistake type
                  <input
                    list="mistake-types"
                    value={reviewDraft.mistake_type}
                    onChange={(event) => setReviewDraft((draft) => ({ ...draft, mistake_type: event.target.value }))}
                    placeholder="region confusion"
                  />
                  <datalist id="mistake-types">
                    {mistakeTypeOptions.map((mistakeType) => (
                      <option key={mistakeType} value={mistakeType} />
                    ))}
                  </datalist>
                </label>

                <label>
                  Tags
                  <input
                    value={reviewDraft.tagsText}
                    onChange={(event) => setReviewDraft((draft) => ({ ...draft, tagsText: event.target.value }))}
                    placeholder="bollards, dry climate, road signs"
                  />
                </label>

                <label>
                  Notes
                  <textarea
                    value={reviewDraft.manual_notes}
                    onChange={(event) => setReviewDraft((draft) => ({ ...draft, manual_notes: event.target.value }))}
                    rows={5}
                    placeholder="What made this round tricky?"
                  />
                </label>

                <button className="primary-button" type="button" onClick={saveRoundReview}>Save review</button>
                {reviewStatus ? <p className="muted">{reviewStatus}</p> : null}
              </>
            ) : (
              <p className="muted">No rounds available to review.</p>
            )}
          </aside>
        </div>
      </Section>

      <Section title="Country performance">
        <SimpleTable
          columns={[
            { key: 'actual_country', label: 'Country' },
            { key: 'rounds_played', label: 'Rounds' },
            { key: 'avg_score', label: 'Avg Score', render: (value) => formatNumber(value, 0) },
            { key: 'median_distance_km', label: 'Median Dist (km)', render: (value) => formatNumber(value, 1) },
            { key: 'correct_country_rate', label: 'Correct Rate', render: (value) => value == null ? '-' : `${formatNumber(value * 100, 1)}%` },
          ]}
          rows={countryPerformance}
        />
      </Section>

      <div className="grid two-up">
        <Section title="Region performance">
          <SimpleTable
            columns={[
              { key: 'country', label: 'Country' },
              { key: 'region', label: 'Region' },
              { key: 'rounds_played', label: 'Rounds' },
              { key: 'avg_score', label: 'Avg Score', render: (value) => formatNumber(value, 0) },
              { key: 'correct_region_rate', label: 'Correct Region', render: (value) => value == null ? '-' : `${formatNumber(value * 100, 1)}%` },
            ]}
            rows={regionPerformance}
          />
        </Section>

        <Section title="Region confusion">
          <SimpleTable
            columns={[
              { key: 'actual_region', label: 'Actual Region', render: (value, row) => `${row.actual_country ?? ''} ${value ?? ''}`.trim() },
              { key: 'guessed_region', label: 'Guessed Region', render: (value, row) => `${row.guessed_country ?? ''} ${value ?? ''}`.trim() },
              { key: 'count', label: 'Count' },
            ]}
            rows={regionConfusionMatrix}
          />
        </Section>
      </div>

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
