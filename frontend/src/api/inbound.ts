import { get, post, put, del } from '@/utils/request'
import type { InboundRecord, InboundFormData, InboundQuery } from '@/types/inventory'

export function getInboundList(params: InboundQuery) {
  return get<{ list: InboundRecord[]; total: number; page: number; per_page: number; pages: number }>('/inbound', params)
}

export function getInbound(id: number) {
  return get<InboundRecord>(`/inbound/${id}`)
}

export function createInbound(data: InboundFormData) {
  return post<InboundRecord>('/inbound', data)
}

export function updateInbound(id: number, data: Partial<InboundFormData>) {
  return put<InboundRecord>(`/inbound/${id}`, data)
}

export function deleteInbound(id: number) {
  return del(`/inbound/${id}`)
}

export function exportInbound(params: InboundQuery) {
  return get<Blob>('/inbound/export', params, { responseType: 'blob' })
}