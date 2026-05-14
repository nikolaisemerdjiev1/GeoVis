import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function useDashboardData() {
  const [data, setData] = useState({
    loading: true,
    error: null,
    health: null,
    recentGames: [],
    recentImports: [],
    roundReviews: [],
    reviewOptions: { mistake_types: [], tags: [] },
    reviewQueue: { recent_misses: [], recurring_confusions: [], tagged_rounds: [] },
    countryPerformance: [],
    regionPerformance: [],
    confusionMatrix: [],
    regionConfusionMatrix: [],
    practicePriorities: [],
  })

  useEffect(() => {
    async function load() {
      try {
        const [
          health,
          recentGames,
          recentImports,
          roundReviews,
          reviewOptions,
          reviewQueue,
          countryPerformance,
          regionPerformance,
          confusionMatrix,
          regionConfusionMatrix,
          practicePriorities,
        ] = await Promise.all([
          api.health(),
          api.recentGames(),
          api.recentImports(),
          api.roundReviews(),
          api.reviewOptions(),
          api.reviewQueue(),
          api.countryPerformance(),
          api.regionPerformance(),
          api.confusionMatrix(),
          api.regionConfusionMatrix(),
          api.practicePriorities(),
        ])

        setData({
          loading: false,
          error: null,
          health,
          recentGames,
          recentImports,
          roundReviews,
          reviewOptions,
          reviewQueue,
          countryPerformance,
          regionPerformance,
          confusionMatrix,
          regionConfusionMatrix,
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
