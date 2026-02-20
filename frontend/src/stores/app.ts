import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref<boolean>(
    localStorage.getItem('sidebarCollapsed') === 'true'
  )
  
  const theme = ref<string>(localStorage.getItem('theme') || 'light')
  const language = ref<string>(localStorage.getItem('language') || 'zh-CN')
  const device = ref<'desktop' | 'mobile'>('desktop')
  const breadcrumbs = ref<Array<{ title: string; path?: string }>>([])
  const loading = ref<boolean>(false)
  
  const isMobile = computed(() => device.value === 'mobile')
  const isDark = computed(() => theme.value === 'dark')
  
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed.value))
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    applyTheme()
  }
  
  const applyTheme = () => {
    const html = document.documentElement
    if (theme.value === 'dark') {
      html.classList.add('dark')
      html.setAttribute('data-theme', 'dark')
    } else {
      html.classList.remove('dark')
      html.setAttribute('data-theme', 'light')
    }
  }
  
  const initApp = () => {
    applyTheme()
    const checkDevice = () => {
      const width = window.innerWidth
      device.value = width < 768 ? 'mobile' : 'desktop'
    }
    checkDevice()
    window.addEventListener('resize', checkDevice)
  }
  
  return {
    sidebarCollapsed, theme, language, device, breadcrumbs, loading,
    isMobile, isDark, toggleSidebar, toggleTheme, initApp
  }
})