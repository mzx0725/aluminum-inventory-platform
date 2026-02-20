export type TaskStatus = 'pending' | 'in_progress' | 'completed'
export type TaskPriority = 'high' | 'medium' | 'low'

export interface Task {
  id: number
  title: string
  description: string
  assignee_id: number | null
  assignee: string | null
  creator_id: number
  creator: string
  status: TaskStatus
  priority: TaskPriority
  due_date: string | null
  created_at: string
  completed_at: string | null
}

export interface TaskFormData {
  title: string
  description: string
  assignee_id: number | null
  creator_id: number
  priority: TaskPriority
  due_date: string | null
}

export interface TaskQuery {
  page?: number
  per_page?: number
  status?: TaskStatus
  priority?: TaskPriority
  assignee_id?: number
}

export interface TaskStatusUpdate {
  status: TaskStatus
}

export interface TaskAssignUpdate {
  assignee_id: number
}