function findNextData() {
  const script = document.getElementById('__NEXT_DATA__')
  if (!script?.textContent) return null

  try {
    return JSON.parse(script.textContent)
  } catch {
    return null
  }
}

function isObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
}

function firstNumber(...values) {
  for (const value of values) {
    if (typeof value === 'number' && Number.isFinite(value)) return value
    if (typeof value === 'string' && value.trim() !== '') {
      const parsed = Number(value.replace(/,/g, ''))
      if (Number.isFinite(parsed)) return parsed
    }
  }
  return null
}

function firstString(...values) {
  for (const value of values) {
    if (typeof value === 'string' && value.trim() !== '') return value.trim()
  }
  return null
}

function parseDate(...values) {
  for (const value of values) {
    if (!value) continue
    const date = new Date(value)
    if (!Number.isNaN(date.valueOf())) return date.toISOString()
  }
  return new Date().toISOString()
}

function scoreFrom(...values) {
  const expanded = values.flatMap((value) => [value?.amount, value?.score, value])
  const score = firstNumber(...expanded)
  return score == null ? null : Math.round(score)
}

function normalizeDistanceKm(...values) {
  const meters = firstNumber(
    ...values.flatMap((value) => [value?.distanceInMeters, value?.distanceMeters, value?.distance?.meters]),
  )
  if (meters != null) return meters / 1000

  return firstNumber(...values.flatMap((value) => [value?.distanceInKm, value?.distanceKm, value?.distance?.kilometers]))
}

function coordinatesFrom(...values) {
  for (const value of values) {
    if (!isObject(value)) continue

    const lat = firstNumber(value.lat, value.latitude)
    const lng = firstNumber(value.lng, value.lon, value.long, value.longitude)
    if (lat != null && lng != null) return { lat, lng }
  }

  return { lat: null, lng: null }
}

function lastGuess(round, playerGuess = null) {
  if (Array.isArray(round.guesses) && round.guesses.length > 0) {
    return round.guesses[round.guesses.length - 1]
  }
  return round.guess ?? round.playerGuess ?? round.selectedGuess ?? playerGuess
}

function guessIfResultsPage() {
  const path = window.location.pathname.toLowerCase()
  return path.includes('/results') || path.includes('/summary')
}

function gameIdFromUrl() {
  const match = window.location.pathname.match(/\/(?:game|results|challenge)\/([^/?#]+)/i)
  return match?.[1] ?? null
}

function collectGameCandidates(root) {
  const candidates = []
  const seen = new WeakSet()
  const queue = [{ value: root, depth: 0 }]

  while (queue.length > 0) {
    const { value, depth } = queue.shift()
    if (!isObject(value) && !Array.isArray(value)) continue
    if (seen.has(value)) continue
    seen.add(value)

    if (isObject(value) && Array.isArray(value.rounds) && value.rounds.length > 0) {
      candidates.push(value)
    }

    if (depth >= 8) continue

    const entries = Array.isArray(value) ? value : Object.values(value)
    for (const child of entries) {
      if (isObject(child) || Array.isArray(child)) queue.push({ value: child, depth: depth + 1 })
    }
  }

  return candidates
}

function roundLooksCompleted(round) {
  if (!isObject(round)) return false
  return Boolean(
    lastGuess(round) ||
      round.score != null ||
      round.roundScore != null ||
      round.distanceInMeters != null ||
      round.distanceMeters != null ||
      round.distanceKm != null,
  )
}

function gameLooksCompleted(game) {
  const status = firstString(game.state, game.status, game.phase, game.gameState)?.toLowerCase()
  if (['finished', 'complete', 'completed', 'ended'].includes(status)) return true
  if (game.totalScore != null || game.finalScore != null || game.player?.totalScore != null) return true

  return Array.isArray(game.rounds) && game.rounds.length > 0 && game.rounds.every(roundLooksCompleted)
}

function playerGuessForRound(game, index) {
  if (Array.isArray(game.player?.guesses)) return game.player.guesses[index] ?? null
  if (Array.isArray(game.player?.rounds)) return game.player.rounds[index]?.guess ?? game.player.rounds[index] ?? null

  const currentPlayerId = game.player?.id ?? game.player?.userId
  const participant = Array.isArray(game.participants)
    ? game.participants.find((item) => item.id === currentPlayerId || item.userId === currentPlayerId) ?? game.participants[0]
    : null

  if (Array.isArray(participant?.guesses)) return participant.guesses[index] ?? null
  return null
}

function mapRound(game, round, index) {
  const playerGuess = playerGuessForRound(game, index)
  const actual = coordinatesFrom(round, round.location, round.panorama, round.answer)
  const guessed = lastGuess(round, playerGuess)
  const guess = coordinatesFrom(guessed, round.guess, round.playerGuess, round.selectedGuess, playerGuess)

  return {
    round_number: firstNumber(round.roundNumber, round.round_number, round.number) ?? index + 1,
    actual_lat: actual.lat,
    actual_lng: actual.lng,
    guess_lat: guess.lat,
    guess_lng: guess.lng,
    actual_country: firstString(
      round.actualCountry,
      round.actual_country,
      round.country,
      round.countryName,
      round.countryCode,
      round.streakLocationCode,
      round.location?.country,
      round.location?.countryCode,
    ),
    guessed_country: firstString(
      guessed?.country,
      guessed?.countryCode,
      round.guessedCountry,
      round.guessed_country,
      round.guess?.country,
      round.guess?.countryCode,
    ),
    actual_region: firstString(round.actualRegion, round.actual_region, round.region, round.location?.region),
    guessed_region: firstString(guessed?.region, round.guessedRegion, round.guessed_region),
    distance_km: normalizeDistanceKm(round, guessed, playerGuess),
    score: scoreFrom(round.score, round.roundScore, guessed?.score, guessed?.roundScore, playerGuess?.score, playerGuess?.roundScore),
    guess_time_sec: firstNumber(
      round.guessTimeSeconds,
      round.guess_time_sec,
      round.time,
      round.timeTaken,
      guessed?.time,
      guessed?.timeTaken,
      playerGuess?.time,
      playerGuess?.timeTaken,
    ),
    movement_allowed: typeof round.movementAllowed === 'boolean' ? round.movementAllowed : null,
    timer_sec: firstNumber(round.timerSeconds, round.timer_sec, round.timeLimit),
  }
}

function mapGame(game, detectedAt) {
  const rounds = game.rounds
    .map((round, index) => mapRound(game, round, index))
    .filter(
      (round) =>
        round.score != null ||
        round.distance_km != null ||
        round.guess_lat != null ||
        round.guess_lng != null,
    )

  return {
    external_game_id: firstString(game.token, game.id, game.gameId, game.challengeToken, gameIdFromUrl()),
    played_at: parseDate(game.finishedAt, game.completedAt, game.updatedAt, game.createdAt, game.startedAt, detectedAt),
    mode: firstString(game.mode, game.type, game.gameMode),
    map_name: firstString(game.mapName, game.map?.name, game.map?.title, game.mapSlug),
    total_score: scoreFrom(game.totalScore ?? game.finalScore ?? game.score ?? game.player?.totalScore),
    total_distance_km:
      firstNumber(game.totalDistanceInMeters, game.distanceInMeters) != null
        ? firstNumber(game.totalDistanceInMeters, game.distanceInMeters) / 1000
        : firstNumber(game.totalDistanceKm, game.distanceKm),
    result_text: firstString(game.resultText, game.outcome, game.status, game.state) ?? 'Completed',
    rating_before: scoreFrom(game.ratingBefore, game.player?.ratingBefore),
    rating_after: scoreFrom(game.ratingAfter, game.player?.ratingAfter),
    rounds,
  }
}

function findCompletedGame(nextData, detectedAt) {
  if (!nextData) return null

  const directGame = nextData.props?.pageProps?.preselectedGame
  const candidates = directGame ? [directGame, ...collectGameCandidates(nextData)] : collectGameCandidates(nextData)

  return candidates
    .filter(gameLooksCompleted)
    .map((game) => mapGame(game, detectedAt))
    .filter((game) => game.rounds.length > 0)
    .sort((a, b) => b.rounds.length - a.rounds.length)[0] ?? null
}

function extractCompletedGameData() {
  const detectedAt = new Date().toISOString()
  const nextData = findNextData()
  const isLikelyResultsPage = guessIfResultsPage()
  const game = isLikelyResultsPage ? findCompletedGame(nextData, detectedAt) : null

  return {
    detectedAt,
    pageUrl: window.location.href,
    title: document.title,
    isLikelyResultsPage,
    parsedGame: game,
    nextDataKeys: nextData ? Object.keys(nextData) : [],
  }
}

window.GeoVISParser = { extractCompletedGameData }
