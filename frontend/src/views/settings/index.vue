<template>
  <div class="settings-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>外观设置</span>
            </div>
          </template>
          
          <el-form label-width="100px" class="settings-form">
            <el-form-item label="主题模式">
              <el-radio-group v-model="themeMode" @change="handleThemeChange">
                <el-radio-button value="light">
                  <el-icon><Sunny /></el-icon>
                  浅色模式
                </el-radio-button>
                <el-radio-button value="dark">
                  <el-icon><Moon /></el-icon>
                  深色模式
                </el-radio-button>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="侧边栏">
              <el-switch
                v-model="sidebarCollapsed"
                active-text="折叠"
                inactive-text="展开"
                @change="handleSidebarChange"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>系统信息</span>
            </div>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">
              铝板智慧物料管控平台
            </el-descriptions-item>
            <el-descriptions-item label="系统版本">
              v1.0.0
            </el-descriptions-item>
            <el-descriptions-item label="前端框架">
              Vue 3 + TypeScript + Element Plus
            </el-descriptions-item>
            <el-descriptions-item label="后端框架">
              Flask + SQLAlchemy
            </el-descriptions-item>
            <el-descriptions-item label="数据库">
              SQLite
            </el-descriptions-item>
            <el-descriptions-item label="当前时间">
              {{ currentTime }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Bell /></el-icon>
              <span>通知设置</span>
            </div>
          </template>
          
          <el-form label-width="120px" class="settings-form">
            <el-form-item label="库存预警通知">
              <el-switch v-model="notificationSettings.lowStock" />
              <span class="setting-desc">当库存低于预警阈值时发送通知</span>
            </el-form-item>
            
            <el-form-item label="任务到期提醒">
              <el-switch v-model="notificationSettings.taskDue" />
              <span class="setting-desc">任务即将到期时发送提醒</span>
            </el-form-item>
            
            <el-form-item label="出库审批通知">
              <el-switch v-model="notificationSettings.outboundApproval" />
              <span class="setting-desc">有新的出库申请时发送通知</span>
            </el-form-item>
            
            <el-form-item label="系统公告通知">
              <el-switch v-model="notificationSettings.systemNotice" />
              <span class="setting-desc">接收系统公告和更新通知</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>数据设置</span>
            </div>
          </template>
          
          <el-form label-width="120px" class="settings-form">
            <el-form-item label="分页大小">
              <el-select v-model="pageSize" @change="handlePageSizeChange">
                <el-option :value="10" label="10 条/页" />
                <el-option :value="20" label="20 条/页" />
                <el-option :value="50" label="50 条/页" />
                <el-option :value="100" label="100 条/页" />
              </el-select>
              <span class="setting-desc">列表默认每页显示数据条数</span>
            </el-form-item>
            
            <el-form-item label="库存预警阈值">
              <el-input-number
                v-model="warningThreshold"
                :min="1"
                :max="1000"
                @change="handleThresholdChange"
              />
              <span class="setting-desc">库存数量低于此值时显示预警</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, Sunny, Moon, InfoFilled, Bell, Document } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const themeMode = ref('light')
const sidebarCollapsed = ref(false)
const pageSize = ref(10)
const warningThreshold = ref(10)
const currentTime = ref('')

const notificationSettings = reactive({
  lowStock: true,
  taskDue: true,
  outboundApproval: true,
  systemNotice: true
})

let timeInterval: number | null = null

const updateTime = () => {
  const now = new Date()
  const options: Intl.DateTimeFormatOptions = {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }
  currentTime.value = now.toLocaleString('zh-CN', options)
}

const handleThemeChange = (value: string) => {
  appStore.setTheme(value)
  ElMessage.success(`已切换到${value === 'dark' ? '深色' : '浅色'}模式`)
}

const handleSidebarChange = (value: boolean) => {
  appStore.setSidebarCollapsed(value)
}

const handlePageSizeChange = () => {
  localStorage.setItem('pageSize', String(pageSize.value))
  ElMessage.success('设置已保存')
}

const handleThresholdChange = () => {
  localStorage.setItem('warningThreshold', String(warningThreshold.value))
  ElMessage.success('设置已保存')
}

onMounted(() => {
  themeMode.value = appStore.theme
  sidebarCollapsed.value = appStore.sidebarCollapsed
  pageSize.value = parseInt(localStorage.getItem('pageSize') || '10')
  warningThreshold.value = parseInt(localStorage.getItem('warningThreshold') || '10')
  
  updateTime()
  timeInterval = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped lang="scss">
.settings-page {
  padding: 0;
}

.settings-card {
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 500;
  }
}

.settings-form {
  .setting-desc {
    margin-left: 12px;
    color: var(--text-color-secondary);
    font-size: 12px;
  }
}

.mt-20 {
  margin-top: 20px;
}
</style>
