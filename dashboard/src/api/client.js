const API_BASE = 'http://127.0.0.1:8000'

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

export const api = {
  health: () => getJson('/health'),
  recentGames: () => getJson('/api/games/recent'),
  countryPerformance: () => getJson('/api/analytics/country-performance'),
  confusionMatrix: () => getJson('/api/analytics/confusion-matrix'),
  scoreTrend: () => getJson('/api/analytics/score-trend'),
  practicePriorities: () => getJson('/api/analytics/practice-priorities'),
}
