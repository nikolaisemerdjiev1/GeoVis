async function init() {
  const capture = window.GeoVISParser.extractCompletedGameData()

  if (!capture.isLikelyResultsPage) {
    return
  }

  await window.GeoVISStorage.saveLastCapture(capture)

  if (!capture.parsedGame) {
    console.info('GeoVIS found a results page but could not parse a completed game.', capture)
    return
  }

  console.info('GeoVIS parsed completed game result.', capture.parsedGame)

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
