import { get, post, put, del } from '@/utils/request'

export interface Plate {
  id: number
  model: string
  specification: string
  unit: string
  supplier: string
  remark: string
}

export interface PlateQuery {
  page?: number
  per_page?: number
  search?: string
}

export interface PlateFormData {
  model: string
  specification: string
  unit?: string
  supplier?: string
  remark?: string
}

export function getPlateList(params: PlateQuery) {
  return get<{ list: Plate[]; total: number }>('/plates', params)
}

export function getPlateDetail(id: number) {
  return get<Plate>(`/plates/${id}`)
}

export function createPlate(data: PlateFormData) {
  return post<Plate>('/plates', data)
}

export function updatePlate(id: number, data: PlateFormData) {
  return put<Plate>(`/plates/${id}`, data)
}

export function deletePlate(id: number) {
  return del<{ message: string }>(`/plates/${id}`)
}