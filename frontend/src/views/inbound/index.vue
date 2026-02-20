<template>
  <div class="inbound-container">
    <el-card class="search-card">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :shortcuts="dateShortcuts"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item label="铝板型号">
          <el-input v-model="queryParams.plate_model" placeholder="请输入铝板型号" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="queryParams.batch_number" placeholder="请输入批次号" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="queryParams.supplier" placeholder="请输入供应商" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>入库记录列表</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              入库登记
            </el-button>
            <el-button type="success" @click="handleExport" :loading="exportLoading">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="铝板型号" width="150">
          <template #default="{ row }">
            {{ row.plate?.model || '-' }} / {{ row.plate?.specification || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="入库数量" width="120">
          <template #default="{ row }">
            <el-tag type="success">{{ row.quantity }} {{ row.plate?.unit || '张' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="batch_number" label="批次号" width="150" />
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column prop="operator_name" label="操作员" width="120" />
        <el-table-column prop="inbound_time" label="入库时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.inbound_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      title="入库登记"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="铝板" prop="plate_id">
          <el-select
            v-model="formData.plate_id"
            placeholder="请选择铝板"
            filterable
            style="width: 100%"
            :loading="plateLoading"
          >
            <el-option
              v-for="plate in plateList"
              :key="plate.id"
              :label="`${plate.model} - ${plate.specification}`"
              :value="plate.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number v-model="formData.quantity" :min="1" :max="999999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="批次号" prop="batch_number">
          <el-input v-model="formData.batch_number" placeholder="请输入批次号" />
        </el-form-item>
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="formData.supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getInboundList, createInbound, type InboundRecord, type InboundFormData, type InboundQuery } from '@/api/inbound'
import { getPlateList, type Plate } from '@/api/plate'
import { useUserStore } from '@/stores/user'
import { formatDateTime } from '@/utils/format'

const userStore = useUserStore()

const loading = ref(false)
const exportLoading = ref(false)
const submitLoading = ref(false)
const plateLoading = ref(false)
const tableData = ref<InboundRecord[]>([])
const plateList = ref<Plate[]>([])
const total = ref(0)
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()

const dateRange = ref<[string, string] | null>(null)

const queryParams = reactive<InboundQuery>({
  page: 1,
  per_page: 10,
  plate_model: '',
  batch_number: '',
  supplier: ''
})

const formData = reactive<InboundFormData & { remark?: string }>({
  plate_id: 0,
  quantity: 1,
  batch_number: '',
  supplier: '',
  remark: ''
})

const formRules: FormRules = {
  plate_id: [{ required: true, message: '请选择铝板', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入入库数量', trigger: 'blur' }],
  batch_number: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  supplier: [{ required: true, message: '请输入供应商', trigger: 'blur' }]
}

const dateShortcuts = [
  {
    text: '今天',
    value: () => {
      const today = new Date()
      return [today, today]
    }
  },
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  }
]

const fetchData = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_date = dateRange.value[0]
      queryParams.end_date = dateRange.value[1]
    } else {
      queryParams.start_date = undefined
      queryParams.end_date = undefined
    }
    
    const res = await getInboundList(queryParams)
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取入库记录失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchPlateList = async () => {
  plateLoading.value = true
  try {
    const res = await getPlateList({ per_page: 1000 })
    plateList.value = res.list || []
  } catch (error) {
    console.error('获取铝板列表失败:', error)
  } finally {
    plateLoading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  fetchData()
}

const handleReset = () => {
  dateRange.value = null
  queryParams.plate_model = ''
  queryParams.batch_number = ''
  queryParams.supplier = ''
  queryParams.page = 1
  fetchData()
}

const handleSizeChange = (size: number) => {
  queryParams.per_page = size
  fetchData()
}

const handleCurrentChange = (page: number) => {
  queryParams.page = page
  fetchData()
}

const handleAdd = () => {
  formData.plate_id = 0
  formData.quantity = 1
  formData.batch_number = ''
  formData.supplier = ''
  formData.remark = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitLoading.value = true
  try {
    const submitData = {
      plate_id: formData.plate_id,
      quantity: formData.quantity,
      batch_number: formData.batch_number,
      supplier: formData.supplier,
      remark: formData.remark,
      operator_name: userStore.userInfo?.real_name || '未知操作员'
    }
    await createInbound(submitData)
    ElMessage.success('入库登记成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('入库登记失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleExport = async () => {
  exportLoading.value = true
  try {
    const params: InboundQuery = { ...queryParams }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const url = new URL('http://127.0.0.1:5000/api/inbound/export')
    Object.keys(params).forEach(key => {
      if (params[key as keyof InboundQuery]) {
        url.searchParams.append(key, String(params[key as keyof InboundQuery]))
      }
    })
    
    const link = document.createElement('a')
    link.href = url.toString()
    link.setAttribute('download', `入库记录_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchPlateList()
})
</script>

<style scoped lang="scss">
.inbound-container {
  padding: 20px;
  
  .search-card {
    margin-bottom: 20px;
    
    .search-form {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
  }
  
  .table-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-buttons {
        display: flex;
        gap: 10px;
      }
    }
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
