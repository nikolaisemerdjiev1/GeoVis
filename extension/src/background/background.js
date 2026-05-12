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
  const response = await fetch(`${API_BASE}/health`)
  if (!response.ok) {
    throw new Error('Backend is not reachable')
  }

  return { accepted: true, previewOnly: true, payload }
}
