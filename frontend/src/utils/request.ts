import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    if (response.config.responseType === 'blob') {
      return response
    }
    if (response.status >= 200 && response.status < 300) {
      return res
    }
    return res
  },
  (error) => {
    console.error('Response error:', error)
    let message = '请求失败'
    let shouldShowError = true
    
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          message = data?.error || '请求参数错误'
          break
        case 401:
          message = data?.error || '未授权，请重新登录'
          const userStore = useUserStore()
          userStore.clearAuth()
          window.location.href = '/login'
          break
        case 403:
          message = data?.error || '拒绝访问'
          break
        case 404:
          message = '请求资源不存在'
          shouldShowError = false
          break
        case 500:
          message = '服务器内部错误'
          shouldShowError = false
          break
        default:
          message = data?.error || data?.message || '请求失败'
      }
    } else if (error.message.includes('timeout')) {
      message = '请求超时'
    } else if (error.message.includes('Network')) {
      message = '网络错误，请检查网络连接'
      shouldShowError = false
    }
    
    if (shouldShowError) {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export function get<T>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, { params, ...config })
}

export function post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config)
}

export function put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.put(url, data, config)
}

export function del<T>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, { params, ...config })
}

export function download(url: string, params?: any, filename?: string): Promise<void> {
  return service.get(url, {
    params,
    responseType: 'blob'
  }).then((response: any) => {
    const blob = new Blob([response.data])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename || 'download'
    link.click()
    URL.revokeObjectURL(link.href)
  })
}

export default service