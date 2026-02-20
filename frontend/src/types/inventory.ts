// 库存相关类型定义

export interface Inventory {
  id: number
  plate_id: number
  plateCode: string
  specification: string
  material: string
  totalQuantity: number
  availableQuantity: number
  reservedQuantity: number
  defectiveQuantity: number
  location: string
  batchNumber: string
  warningThreshold: number
  unit: string
  supplier: string
  lastInboundAt?: string
  lastOutboundAt?: string
  updatedAt: string
}

export interface InventoryQuery {
  page?: number
  per_page?: number
  plateCode?: string
  specification?: string
  material?: string
  location?: string
  batchNumber?: string
  low_stock?: boolean
}

// 入库记录
export interface InboundRecord {
  id: number
  inboundCode: string
  plateId: number
  plateCode: string
  specification: string
  quantity: number
  weight: number
  supplier: string
  batchNumber: string
  location: string
  operator: string
  inspector?: string
  qualityStatus: QualityStatus
  remark?: string
  createdAt: string
}

export type QualityStatus = 'qualified' | 'unqualified' | 'pending'

export interface InboundQuery {
  page?: number
  pageSize?: number
  inboundCode?: string
  plateCode?: string
  supplier?: string
  qualityStatus?: QualityStatus
  startDate?: string
  endDate?: string
}

export interface InboundFormData {
  id?: number
  plateId: number
  quantity: number
  supplier: string
  batchNumber: string
  location: string
  inspector?: string
  qualityStatus: QualityStatus
  remark?: string
}

// 出库记录
export interface OutboundRecord {
  id: number
  outboundCode: string
  plateId: number
  plateCode: string
  specification: string
  quantity: number
  weight: number
  customer?: string
  orderNumber?: string
  location: string
  applicant: string      // 申请人
  approver?: string      // 审批人
  status: OutboundStatus // 状态
  remark?: string
  createdAt: string
}

export type OutboundStatus = 'pending' | 'approved' | 'rejected'

export interface OutboundQuery {
  page?: number
  per_page?: number
  outboundCode?: string
  plateCode?: string
  customer?: string
  status?: OutboundStatus
  startDate?: string
  endDate?: string
}

export interface OutboundFormData {
  id?: number
  plateId?: number
  quantity: number
  customer?: string
  orderNumber?: string
  remark?: string
}

// 库存预警
export interface InventoryAlert {
  id: number
  plateCode: string
  specification: string
  alertType: AlertType
  currentValue: number
  thresholdValue: number
  message: string
  status: AlertStatus
  createdAt: string
}

export type AlertType = 'low_stock' | 'over_stock' | 'expiring' | 'defective'
export type AlertStatus = 'active' | 'resolved' | 'ignored'
