import { get, post, put, del } from '@/utils/request'
import type { Task, TaskFormData, TaskQuery, TaskStatusUpdate, TaskAssignUpdate } from '@/types/task'

export function getTaskList(params: TaskQuery): Promise<{ tasks: Task[]; total: number }> {
  return get('/tasks', params)
}

export function getTaskDetail(id: number): Promise<Task> {
  return get(`/tasks/${id}`)
}

export function createTask(data: TaskFormData): Promise<Task> {
  return post('/tasks', data)
}

export function updateTask(id: number, data: TaskFormData): Promise<Task> {
  return put(`/tasks/${id}`, data)
}

export function deleteTask(id: number): Promise<void> {
  return del(`/tasks/${id}`)
}

export function updateTaskStatus(id: number, data: TaskStatusUpdate): Promise<Task> {
  return put(`/tasks/${id}/status`, data)
}

export function assignTask(id: number, data: TaskAssignUpdate): Promise<Task> {
  return put(`/tasks/${id}/assign`, data)
}