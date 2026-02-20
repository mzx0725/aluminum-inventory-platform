import { post, get, put, del } from '@/utils/request'
import type { LoginForm, LoginResponse, User, UserQuery, UserFormData } from '@/types/user'

export function loginApi(data: LoginForm): Promise<LoginResponse> {
  return post<LoginResponse>('/auth/login', data)
}

export function logoutApi(): Promise<void> {
  return post<void>('/auth/logout')
}

export function getUserInfoApi(): Promise<User> {
  return get<User>('/auth/userinfo')
}

export function getUserListApi(params: UserQuery): Promise<{ list: User[]; total: number }> {
  return get<{ list: User[]; total: number }>('/auth/users', params)
}

export function createUserApi(data: UserFormData): Promise<{ user: User; message: string }> {
  return post<{ user: User; message: string }>('/auth/register', data)
}

export function registerApi(data: { username: string; real_name: string; password: string; role: string; status: string }): Promise<{ user: User; message: string }> {
  return post<{ user: User; message: string }>('/auth/register', data)
}

export function updateUserApi(id: number, data: Partial<UserFormData>): Promise<{ user: User; message: string }> {
  return put<{ user: User; message: string }>(`/auth/users/${id}`, data)
}

export function deleteUserApi(id: number): Promise<{ message: string }> {
  return del<{ message: string }>(`/auth/users/${id}`)
}

export function resetPasswordApi(id: number): Promise<{ password: string }> {
  return post<{ password: string }>(`/auth/users/${id}/reset-password`)
}