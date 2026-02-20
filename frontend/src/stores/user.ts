import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginForm } from '@/types/user'
import { loginApi, getUserInfoApi, logoutApi } from '@/api/user'

const TOKEN_KEY = 'aluminum_token'
const USER_KEY = 'aluminum_user'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const userInfo = ref<User | null>(null)
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const username = computed(() => userInfo.value?.username || '')
  const realName = computed(() => userInfo.value?.real_name || '')
  const userRole = computed(() => userInfo.value?.role || '')

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }

  const setUser = (user: User) => {
    userInfo.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  const clearAuth = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  const login = async (loginForm: LoginForm) => {
    try {
      const res = await loginApi(loginForm)
      if (res && res.token) {
        setToken(res.token)
        if (res.user) {
          setUser(res.user)
        }
        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  const fetchUserInfo = async () => {
    if (!token.value) return null
    try {
      const user = await getUserInfoApi()
      if (user) {
        setUser(user)
        return user
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      clearAuth()
    }
    return null
  }

  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearAuth()
    }
  }

  const initUser = () => {
    const savedUser = localStorage.getItem(USER_KEY)
    if (savedUser) {
      try {
        userInfo.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    }
  }

  initUser()

  return {
    token, userInfo, isLoggedIn, isAdmin, username, realName, userRole,
    setToken, setUser, clearAuth, login, fetchUserInfo, logout
  }
})