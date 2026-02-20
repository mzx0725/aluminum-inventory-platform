import { get, post, put, del } from '@/utils/request'
import type { OutboundRecord, OutboundFormData, OutboundQuery } from '@/types/inventory'

export function getOutboundList(params: OutboundQuery) {
  return get<{ list: OutboundRecord[]; total: number; page: number; per_page: number; pages: number }>('/outbound', params)
}

export function getOutbound(id: number) {
  return get<OutboundRecord>(`/outbound/${id}`)
}

export function createOutbound(data: OutboundFormData) {
  return post<OutboundRecord>('/outbound', data)
}

export function updateOutbound(id: number, data: Partial<OutboundFormData>) {
  return put<OutboundRecord>(`/outbound/${id}`, data)
}

export function deleteOutbound(id: number) {
  return del(`/outbound/${id}`)
}

export function approveOutbound(id: number, data: { status: string; reviewer_remark?: string }) {
  return put<OutboundRecord>(`/outbound/${id}/approve`, data)
}

export function rejectOutbound(id: number, data: { status: string; reviewer_remark?: string }) {
  return put<OutboundRecord>(`/outbound/${id}/reject`, data)
}