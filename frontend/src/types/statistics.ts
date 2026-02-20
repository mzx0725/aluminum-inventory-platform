// 统计相关类型定义

export interface OverviewStats {
  total_inventory: number
  today_inbound: number
  today_outbound: number
  pending_approval: number
  inventory_warning: number
  pending_tasks: number
  pending_outbound?: number
  low_stock_warning?: number
}

export interface InventoryStatistics {
  by_model: ModelStatistics[]
  by_location: LocationStatistics[]
}

export interface ModelStatistics {
  model: string
  count: number
  total_quantity: number
  percentage: number
}

export interface LocationStatistics {
  location: string
  count: number
  total_quantity: number
  percentage: number
}

export interface TrendData {
  dates: string[]
  inbound_data: number[]
  outbound_data: number[]
}

export interface TrendQuery {
  start_date: string
  end_date: string
  type?: 'day' | 'week' | 'month'
}

export interface ReportQuery {
  start_date: string
  end_date: string
  type?: 'inventory' | 'inbound' | 'outbound' | 'all'
}
