import { API_BASE } from '../shared/constants.js'

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'GEOVIS_CAPTURE_READY') {
    void postCapture(message.payload)
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error) => sendResponse({ ok: false, error: error.message }))

    return true
  }

  return false
})

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
