import { get } from '@/utils/request'
import type { StatisticsData, TrendData } from '@/types/statistics'

export function getStatistics() {
  return get<StatisticsData>('/statistics')
}

export function getTrendData(params: { start_date?: string; end_date?: string; type?: string }) {
  return get<TrendData>('/statistics/trend', params)
}