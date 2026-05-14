import { API_BASE } from '../shared/constants.js'

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'GEOVIS_CAPTURE_READY') {
    void postCapture(message.payload)
      .then((result) => {
        void saveImportStatus({
          status: 'success',
          external_game_id: message.payload?.parsedGame?.external_game_id,
          message: 'Backend ingest completed.',
        })
        sendResponse({ ok: true, result })
      })
      .catch((error) => {
        void saveImportStatus({
          status: 'error',
          external_game_id: message.payload?.parsedGame?.external_game_id,
          message: error.message,
        })
        sendResponse({ ok: false, error: error.message })
      })

    return true
  }

  return false
})

async function saveImportStatus(entry) {
  const key = 'geovis_import_status_history'
  const result = await chrome.storage.local.get(key)
  const history = Array.isArray(result[key]) ? result[key] : []
  await chrome.storage.local.set({
    [key]: [
      {
        recordedAt: new Date().toISOString(),
        ...entry,
      },
      ...history,
    ].slice(0, 20),
  })
}

async function postCapture(payload) {
  if (!payload?.parsedGame) {
    return { accepted: false, reason: 'No completed game payload found' }
  }

  const response = await fetch(`${API_BASE}/api/ingest/game`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload.parsedGame),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Backend ingest failed: ${response.status} ${text}`)
  }

  return response.json()
}
