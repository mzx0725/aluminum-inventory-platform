<template>
  <div class="statistics-container">
    <el-row :gutter="20" class="overview-section">
      <el-col :span="4">
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
      
      <el-col :span="4">
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
      
      <el-col :span="4">
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
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.pending_approval }}</p>
              <p class="stat-label">待审核</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.inventory_warning }}</p>
              <p class="stat-label">库存预警</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ overviewData.pending_tasks }}</p>
              <p class="stat-label">待处理任务</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>统计分析</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              style="width: 280px;"
            />
            <el-button type="primary" style="margin-left: 12px;" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出报表
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="chart-section">
        <h4 class="chart-title">出入库趋势</h4>
        <div ref="trendChartRef" style="height: 350px;"></div>
      </div>
      
      <el-divider />
      
      <el-row :gutter="20" class="inventory-charts">
        <el-col :span="12">
          <div class="chart-section">
            <h4 class="chart-title">库存统计 - 按型号</h4>
            <div ref="modelChartRef" style="height: 300px;"></div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-section">
            <h4 class="chart-title">库存统计 - 按位置</h4>
            <div ref="locationChartRef" style="height: 300px;"></div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { Box, Download, Upload, Clock, Warning, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { OverviewStats, InventoryStatistics, TrendData } from '@/types/statistics'
import { getOverview, getInventoryStatistics, getTrendData, exportReport } from '@/api/statistics'

const dateRange = ref<[string, string] | null>(null)

const overviewData = reactive<OverviewStats>({
  total_inventory: 0,
  today_inbound: 0,
  today_outbound: 0,
  pending_approval: 0,
  inventory_warning: 0,
  pending_tasks: 0
})

const trendChartRef = ref<HTMLElement>()
const modelChartRef = ref<HTMLElement>()
const locationChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let modelChart: echarts.ECharts | null = null
let locationChart: echarts.ECharts | null = null

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

const fetchInventoryStatistics = async () => {
  try {
    const res = await getInventoryStatistics()
    if (res) {
      initModelChart(res)
      initLocationChart(res)
    }
  } catch (error) {
    console.error('获取库存统计失败:', error)
  }
}

const fetchTrendData = async () => {
  try {
    const params = {
      start_date: dateRange.value?.[0] || getDefaultStartDate(),
      end_date: dateRange.value?.[1] || getDefaultEndDate()
    }
    const res = await getTrendData(params)
    if (res && res.trends) {
      const trendData: TrendData = {
        dates: res.trends.map((t: any) => t.period),
        inbound_data: res.trends.map((t: any) => t.inbound_quantity),
        outbound_data: res.trends.map((t: any) => t.outbound_quantity)
      }
      initTrendChart(trendData)
    }
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

const getDefaultStartDate = () => {
  const date = new Date()
  date.setDate(date.getDate() - 30)
  return date.toISOString().split('T')[0]
}

const getDefaultEndDate = () => {
  return new Date().toISOString().split('T')[0]
}

const initTrendChart = (data: TrendData) => {
  if (!trendChartRef.value) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartRef.value)
  
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
  
  trendChart.setOption(option)
}

const initModelChart = (data: InventoryStatistics) => {
  if (!modelChartRef.value) return
  
  if (modelChart) {
    modelChart.dispose()
  }
  
  modelChart = echarts.init(modelChartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        name: '库存数量',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data.by_model.map(item => ({
          value: item.total_quantity,
          name: item.model
        }))
      }
    ]
  }
  
  modelChart.setOption(option)
}

const initLocationChart = (data: InventoryStatistics) => {
  if (!locationChartRef.value) return
  
  if (locationChart) {
    locationChart.dispose()
  }
  
  locationChart = echarts.init(locationChartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.by_location.map(item => item.location),
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '库存数量',
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        data: data.by_location.map(item => item.total_quantity)
      }
    ]
  }
  
  locationChart.setOption(option)
}

const handleDateChange = () => {
  fetchTrendData()
}

const handleExport = async () => {
  try {
    await exportReport({
      start_date: dateRange.value?.[0] || getDefaultStartDate(),
      end_date: dateRange.value?.[1] || getDefaultEndDate(),
      type: 'all'
    })
    ElMessage.success('报表导出成功')
  } catch (error) {
    console.error('导出报表失败:', error)
    ElMessage.error('导出报表失败')
  }
}

const handleResize = () => {
  trendChart?.resize()
  modelChart?.resize()
  locationChart?.resize()
}

onMounted(async () => {
  await nextTick()
  
  dateRange.value = [getDefaultStartDate(), getDefaultEndDate()]
  
  await Promise.all([
    fetchOverview(),
    fetchInventoryStatistics(),
    fetchTrendData()
  ])
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  modelChart?.dispose()
  locationChart?.dispose()
})
</script>

<style scoped lang="scss">
.statistics-container {
  .overview-section {
    margin-bottom: 20px;
    
    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        
        .stat-icon {
          width: 50px;
          height: 50px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: #fff;
        }
        
        .stat-info {
          flex: 1;
          margin-left: 12px;
          
          .stat-value {
            font-size: 24px;
            font-weight: 600;
            color: #303133;
            margin: 0;
          }
          
          .stat-label {
            font-size: 12px;
            color: #909399;
            margin: 4px 0 0;
          }
        }
      }
    }
  }
  
  .chart-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-actions {
        display: flex;
        align-items: center;
      }
    }
  }
  
  .chart-section {
    .chart-title {
      margin: 0 0 16px;
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .inventory-charts {
    margin-top: 20px;
  }
}
</style>
