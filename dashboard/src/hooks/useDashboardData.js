import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function useDashboardData() {
  const [data, setData] = useState({
    loading: true,
    error: null,
    health: null,
    recentGames: [],
    countryPerformance: [],
    confusionMatrix: [],
    practicePriorities: [],
  })

  useEffect(() => {
    async function load() {
      try {
        const [health, recentGames, countryPerformance, confusionMatrix, practicePriorities] = await Promise.all([
          api.health(),
          api.recentGames(),
          api.countryPerformance(),
          api.confusionMatrix(),
          api.practicePriorities(),
        ])

        setData({
          loading: false,
          error: null,
          health,
          recentGames,
          countryPerformance,
          confusionMatrix,
          practicePriorities,
        })
      } catch (error) {
        setData((prev) => ({ ...prev, loading: false, error: error.message }))
      }
    }

    load()
  }, [])

  return data
}
