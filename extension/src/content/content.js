async function init() {
  const capture = window.GeoVISParser.extractCompletedGameData()

  if (!capture.isLikelyResultsPage) {
    return
  }

  await window.GeoVISStorage.saveLastCapture(capture)

  if (!capture.parsedGame) {
    await window.GeoVISStorage.saveImportStatus({
      status: 'parse_error',
      pageUrl: capture.pageUrl,
      message: 'Results page detected, but no completed game payload could be parsed.',
    })
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
        void window.GeoVISStorage.saveImportStatus({
          status: 'send_error',
          pageUrl: capture.pageUrl,
          external_game_id: capture.parsedGame.external_game_id,
          message: chrome.runtime.lastError.message,
        })
        console.debug('GeoVIS background message failed:', chrome.runtime.lastError.message)
        return
      }
      void window.GeoVISStorage.saveImportStatus({
        status: response?.ok ? 'posted' : 'post_error',
        pageUrl: capture.pageUrl,
        external_game_id: capture.parsedGame.external_game_id,
        message: response?.ok ? 'Backend ingest accepted the result.' : response?.error ?? 'Unknown ingest failure.',
      })
      console.debug('GeoVIS capture response:', response)
    },
  )
}

void init()
