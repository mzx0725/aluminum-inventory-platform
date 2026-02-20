export type UserRole = 'admin' | 'warehouse' | 'dispatcher'
export type UserStatus = 'active' | 'inactive' | 'disabled'

export interface User {
  id: number
  username: string
  real_name: string
  role: UserRole
  status: UserStatus
  created_at: string
}

export interface LoginForm {
  username: string
  password: string
  remember?: boolean
}

export interface LoginResponse {
  token: string
  user: User
  expiresIn: number
}

export interface UserQuery {
  page?: number
  per_page?: number
  username?: string
  role?: UserRole
  status?: UserStatus
}

export interface UserFormData {
  username: string
  password?: string
  real_name: string
  role: UserRole
  status: UserStatus
}

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: '系统管理员',
  warehouse: '仓库管理员',
  dispatcher: '调度员'
}

export const STATUS_LABELS: Record<UserStatus, string> = {
  active: '正常',
  inactive: '停用',
  disabled: '禁用'
}