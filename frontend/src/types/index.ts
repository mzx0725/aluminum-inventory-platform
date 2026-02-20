// 通用类型定义

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

export interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  fixed?: 'left' | 'right' | boolean
  sortable?: boolean | 'custom'
  formatter?: (row: any, column: any, cellValue: any) => string
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
}

export interface DateRange {
  startDate: string
  endDate: string
}

export interface KeyValue {
  [key: string]: any
}
