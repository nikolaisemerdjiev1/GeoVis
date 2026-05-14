const API_BASE = 'http://127.0.0.1:8000'

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

async function putJson(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

export const api = {
  health: () => getJson('/health'),
  recentGames: () => getJson('/api/games/recent'),
  recentImports: () => getJson('/api/imports/recent'),
  roundReviews: (params = {}) => {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') query.set(key, value)
    })
    const suffix = query.toString() ? `?${query.toString()}` : ''
    return getJson(`/api/rounds/review${suffix}`)
  },
  reviewOptions: () => getJson('/api/rounds/review/options'),
  updateRoundNote: (roundId, payload) => putJson(`/api/rounds/${roundId}/note`, payload),
  reviewQueue: () => getJson('/api/training/review-queue'),
  countryPerformance: () => getJson('/api/analytics/country-performance'),
  regionPerformance: () => getJson('/api/analytics/region-performance'),
  confusionMatrix: () => getJson('/api/analytics/confusion-matrix'),
  regionConfusionMatrix: () => getJson('/api/analytics/region-confusion-matrix'),
  scoreTrend: () => getJson('/api/analytics/score-trend'),
  practicePriorities: () => getJson('/api/analytics/practice-priorities'),
}
