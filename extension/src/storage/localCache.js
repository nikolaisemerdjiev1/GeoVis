const KEY = 'geovis_last_capture'

export async function saveLastCapture(payload) {
  await chrome.storage.local.set({ [KEY]: payload })
}

export async function getLastCapture() {
  const result = await chrome.storage.local.get(KEY)
  return result[KEY] ?? null
}
