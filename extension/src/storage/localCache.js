const KEY = 'geovis_last_capture'

async function saveLastCapture(payload) {
  await chrome.storage.local.set({ [KEY]: payload })
}

async function getLastCapture() {
  const result = await chrome.storage.local.get(KEY)
  return result[KEY] ?? null
}

window.GeoVISStorage = { saveLastCapture, getLastCapture }
