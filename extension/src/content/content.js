import { extractCompletedGameData } from '../parser/extractGameData.js'
import { saveLastCapture } from '../storage/localCache.js'

async function init() {
  const capture = extractCompletedGameData()

  if (!capture.isLikelyResultsPage) {
    return
  }

  await saveLastCapture(capture)

  chrome.runtime.sendMessage(
    {
      type: 'GEOVIS_CAPTURE_READY',
      payload: capture,
    },
    (response) => {
      if (chrome.runtime.lastError) {
        console.debug('GeoVIS background message failed:', chrome.runtime.lastError.message)
        return
      }
      console.debug('GeoVIS capture response:', response)
    },
  )
}

void init()
