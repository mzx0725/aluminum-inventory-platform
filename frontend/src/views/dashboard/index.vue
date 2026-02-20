<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="overview-section">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.total_inventory }}</p>
              <p class="stat-label">总库存</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
              <el-icon><Download /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.today_inbound }}</p>
              <p class="stat-label">今日入库</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
              <el-icon><Upload /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.today_outbound }}</p>
              <p class="stat-label">今日出库</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.inventory_warning }}</p>
              <p class="stat-label">库存预警</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>库存趋势</span>
              <el-radio-group v-model="trendType" size="small" @change="handleTrendTypeChange">
                <el-radio-button label="week">近7天</el-radio-button>
                <el-radio-button label="month">近30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <div ref="chartRef" style="height: 350px;"></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="navigateTo('/inbound')">
              <div class="action-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <el-icon><Download /></el-icon>
              </div>
              <div class="action-info">
                <p class="action-title">入库登记</p>
                <p class="action-desc">新增入库记录</p>
              </div>
            </div>
            
            <div class="action-item" @click="navigateTo('/outbound')">
              <div class="action-icon" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
                <el-icon><Upload /></el-icon>
              </div>
              <div class="action-info">
                <p class="action-title">出库登记</p>
                <p class="action-desc">新增出库记录</p>
              </div>
            </div>
            
            <div class="action-item" @click="navigateTo('/inventory')">
              <div class="action-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><Box /></el-icon>
              </div>
              <div class="action-info">
                <p class="action-title">库存查询</p>
                <p class="action-desc">查看库存详情</p>
              </div>
            </div>
            
            <div class="action-item" @click="navigateTo('/tasks')">
              <div class="action-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon><List /></el-icon>
              </div>
              <div class="action-info">
                <p class="action-title">任务管理</p>
                <p class="action-desc">查看调度任务</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近入库记录</span>
              <el-button type="primary" link @click="navigateTo('/inbound')">
                查看更多
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentInbound" border stripe size="small">
            <el-table-column prop="plate_number" label="铝板编号" width="120" />
            <el-table-column prop="model" label="型号" width="100" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="location" label="存放位置" width="120" />
            <el-table-column prop="created_at" label="入库时间" min-width="140">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近出库记录</span>
              <el-button type="primary" link @click="navigateTo('/outbound')">
                查看更多
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentOutbound" border stripe size="small">
            <el-table-column prop="plate_number" label="铝板编号" width="120" />
            <el-table-column prop="model" label="型号" width="100" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="customer" label="客户" width="120" />
            <el-table-column prop="created_at" label="出库时间" min-width="140">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待处理任务</span>
              <el-button type="primary" link @click="navigateTo('/tasks')">
                查看更多
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="pendingTasks" border stripe size="small">
            <el-table-column prop="title" label="任务标题" min-width="180" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assignee" label="执行人" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="100">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleTaskDetail(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Box, Download, Upload, Warning, List, ArrowRight } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { OverviewStats, TrendData } from '@/types/statistics'
import type { Task } from '@/types/task'
import { getOverview, getTrendData } from '@/api/statistics'
import { get } from '@/utils/request'
import { formatDateTime } from '@/utils/format'

const router = useRouter()

const overviewData = reactive<OverviewStats>({
  total_inventory: 0,
  today_inbound: 0,
  today_outbound: 0,
  pending_approval: 0,
  inventory_warning: 0,
  pending_tasks: 0
})

const trendType = ref<'week' | 'month'>('week')

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const recentInbound = ref<any[]>([])

const recentOutbound = ref<any[]>([])

const pendingTasks = ref<Task[]>([])

const fetchOverview = async () => {
  try {
    const res = await getOverview()
    if (res) {
      overviewData.total_inventory = res.total_inventory || 0
      overviewData.today_inbound = res.today_inbound || 0
      overviewData.today_outbound = res.today_outbound || 0
      overviewData.pending_approval = res.pending_outbound || 0
      overviewData.inventory_warning = res.low_stock_warning || 0
      overviewData.pending_tasks = res.pending_tasks || 0
    }
  } catch (error) {
    console.error('获取概览数据失败:', error)
  }
}

const fetchTrendData = async () => {
  try {
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date()
    if (trendType.value === 'week') {
      startDate.setDate(startDate.getDate() - 7)
    } else {
      startDate.setDate(startDate.getDate() - 30)
    }
    
    const res = await getTrendData({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate
    })
    if (res && res.trends) {
      const trendData: TrendData = {
        dates: res.trends.map((t: any) => t.period),
        inbound_data: res.trends.map((t: any) => t.inbound_quantity),
        outbound_data: res.trends.map((t: any) => t.outbound_quantity)
      }
      initChart(trendData)
    }
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

const fetchRecentInbound = async () => {
  try {
    const res = await get<{ list: any[] }>('/inbound', { page: 1, per_page: 5 })
    if (res && res.list) {
      recentInbound.value = res.list.map((item: any) => ({
        plate_number: item.plateCode || item.plate?.model || '-',
        model: item.plate?.model || '-',
        quantity: item.quantity,
        location: item.location || '-',
        created_at: item.inboundTime || item.inbound_time
      }))
    }
  } catch (error) {
    console.error('获取最近入库记录失败:', error)
  }
}

const fetchRecentOutbound = async () => {
  try {
    const res = await get<{ list: any[] }>('/outbound', { page: 1, per_page: 5 })
    if (res && res.list) {
      recentOutbound.value = res.list.map((item: any) => ({
        plate_number: item.plateCode || item.plate?.model || '-',
        model: item.plate?.model || '-',
        quantity: item.quantity,
        customer: item.customer || '-',
        created_at: item.outboundTime || item.outbound_time
      }))
    }
  } catch (error) {
    console.error('获取最近出库记录失败:', error)
  }
}

const fetchPendingTasks = async () => {
  try {
    const res = await get<{ tasks: Task[]; total: number }>('/tasks', { page: 1, per_page: 5, status: 'pending' })
    console.log('Tasks API response:', res)
    if (res && res.tasks) {
      pendingTasks.value = res.tasks
      console.log('Pending tasks loaded:', pendingTasks.value.length)
    }
  } catch (error) {
    console.error('获取待处理任务失败:', error)
  }
}

const initChart = (data: TrendData) => {
  if (!chartRef.value) return
  
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['入库', '出库'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '入库',
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(17, 153, 142, 0.5)' },
            { offset: 1, color: 'rgba(17, 153, 142, 0.1)' }
          ])
        },
        lineStyle: {
          color: '#11998e',
          width: 2
        },
        itemStyle: {
          color: '#11998e'
        },
        data: data.inbound_data
      },
      {
        name: '出库',
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(235, 51, 73, 0.5)' },
            { offset: 1, color: 'rgba(235, 51, 73, 0.1)' }
          ])
        },
        lineStyle: {
          color: '#eb3349',
          width: 2
        },
        itemStyle: {
          color: '#eb3349'
        },
        data: data.outbound_data
      }
    ]
  }
  
  chart.setOption(option)
}

const handleTrendTypeChange = () => {
  fetchTrendData()
}

const navigateTo = (path: string) => {
  router.push(path)
}

const handleTaskDetail = (row: Task) => {
  router.push(`/tasks?id=${row.id}`)
}

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority] || priority
}

const handleResize = () => {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  
  await Promise.all([
    fetchOverview(),
    fetchTrendData(),
    fetchRecentInbound(),
    fetchRecentOutbound(),
    fetchPendingTasks()
  ])
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  .overview-section {
    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        
        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          color: #fff;
        }
        
        .stat-info {
          flex: 1;
          margin-left: 16px;
          
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #303133;
            margin: 0;
          }
          
          .stat-label {
            font-size: 14px;
            color: #909399;
            margin: 4px 0 0;
          }
        }
      }
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .chart-container {
    width: 100%;
  }
  
  .quick-actions {
    .action-item {
      display: flex;
      align-items: center;
      padding: 16px;
      margin-bottom: 12px;
      background: #f5f7fa;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: #e6e8eb;
        transform: translateX(4px);
      }
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .action-icon {
        width: 48px;
        height: 48px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: #fff;
      }
      
      .action-info {
        flex: 1;
        margin-left: 12px;
        
        .action-title {
          font-size: 16px;
          font-weight: 500;
          color: #303133;
          margin: 0;
        }
        
        .action-desc {
          font-size: 12px;
          color: #909399;
          margin: 4px 0 0;
        }
      }
    }
  }
  
  .overdue {
    color: #f56c6c;
    font-weight: 500;
  }
}
</style>
