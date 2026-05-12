function findNextData() {
  const script = document.getElementById('__NEXT_DATA__')
  if (!script?.textContent) return null

  try {
    return JSON.parse(script.textContent)
  } catch {
    return null
  }
}

function guessIfResultsPage() {
  const path = window.location.pathname
  return path.includes('/results') || path.includes('/summary')
}

export function extractCompletedGameData() {
  const nextData = findNextData()

  return {
    detectedAt: new Date().toISOString(),
    pageUrl: window.location.href,
    title: document.title,
    isLikelyResultsPage: guessIfResultsPage(),
    nextDataKeys: nextData ? Object.keys(nextData) : [],
    rawNextData: nextData,
  }
}
