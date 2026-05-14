const KEY = 'geovis_last_capture'
const IMPORT_STATUS_KEY = 'geovis_import_status_history'

async function saveLastCapture(payload) {
  await chrome.storage.local.set({ [KEY]: payload })
}

async function getLastCapture() {
  const result = await chrome.storage.local.get(KEY)
  return result[KEY] ?? null
}

async function saveImportStatus(entry) {
  const result = await chrome.storage.local.get(IMPORT_STATUS_KEY)
  const history = Array.isArray(result[IMPORT_STATUS_KEY]) ? result[IMPORT_STATUS_KEY] : []
  await chrome.storage.local.set({
    [IMPORT_STATUS_KEY]: [
      {
        recordedAt: new Date().toISOString(),
        ...entry,
      },
      ...history,
    ].slice(0, 20),
  })
}

async function getImportStatusHistory() {
  const result = await chrome.storage.local.get(IMPORT_STATUS_KEY)
  return result[IMPORT_STATUS_KEY] ?? []
}

window.GeoVISStorage = { saveLastCapture, getLastCapture, saveImportStatus, getImportStatusHistory }
