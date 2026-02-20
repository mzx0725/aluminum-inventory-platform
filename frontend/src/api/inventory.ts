import { get, post, put, del } from '@/utils/request'
import type { Inventory, InventoryQuery, InventoryCheck, InventoryCheckFormData } from '@/types/inventory'

export function getInventoryList(params: InventoryQuery) {
  return get<{ list: Inventory[]; total: number; page: number; per_page: number; pages: number }>('/inventory', params)
}

export function getInventory(id: number) {
  return get<Inventory>(`/inventory/${id}`)
}

export function getInventoryByPlate(plateId: number) {
  return get<Inventory>(`/inventory/plate/${plateId}`)
}

export function createInventoryCheck(data: InventoryCheckFormData) {
  return post<InventoryCheck>('/inventory/check', data)
}

export function getInventoryChecks(params: { page?: number; per_page?: number }) {
  return get<{ list: InventoryCheck[]; total: number; page: number; per_page: number; pages: number }>('/inventory/checks', params)
}

export function getInventoryCheck(id: number) {
  return get<InventoryCheck>(`/inventory/check/${id}`)
}