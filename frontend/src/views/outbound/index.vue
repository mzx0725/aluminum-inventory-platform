<template>
  <div class="outbound-container">
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
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item label="铝板型号">
          <el-input v-model="queryParams.plate_model" placeholder="请输入铝板型号" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="客户">
          <el-input v-model="queryParams.customer" placeholder="请输入客户" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
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
          <span>出库记录列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            出库申请
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="铝板型号" width="150">
          <template #default="{ row }">
            {{ row.plate?.model || '-' }} / {{ row.plate?.specification || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="出库数量" width="120">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.quantity }} {{ row.plate?.unit || '张' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="customer" label="客户" width="150" />
        <el-table-column prop="applicant_name" label="申请人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewer_name" label="审批人" width="120">
          <template #default="{ row }">
            {{ row.reviewer_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="outbound_time" label="出库时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.outbound_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
            </template>
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
          </template>
        </el-table-column>
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
      title="出库申请"
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
            @change="handlePlateChange"
          >
            <el-option
              v-for="plate in plateList"
              :key="plate.id"
              :label="`${plate.model} - ${plate.specification}`"
              :value="plate.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="可用库存">
          <el-tag :type="availableStock > 0 ? 'success' : 'danger'">
            {{ availableStock }}
          </el-tag>
        </el-form-item>
        <el-form-item label="出库数量" prop="quantity">
          <el-input-number v-model="formData.quantity" :min="1" :max="availableStock" style="width: 100%" />
        </el-form-item>
        <el-form-item label="客户" prop="customer">
          <el-input v-model="formData.customer" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          提交申请
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      title="出库详情"
      width="500px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="铝板型号">{{ currentRecord?.plate?.model }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ currentRecord?.plate?.specification }}</el-descriptions-item>
        <el-descriptions-item label="出库数量">{{ currentRecord?.quantity }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ currentRecord?.customer }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRecord?.applicant_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord?.status)">
            {{ getStatusText(currentRecord?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审批人">{{ currentRecord?.reviewer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="出库时间">{{ formatDateTime(currentRecord?.outbound_time) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRecord?.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getOutboundList, createOutbound, approveOutbound, rejectOutbound, type OutboundRecord, type OutboundQuery } from '@/api/outbound'
import { getPlateList, type Plate } from '@/api/plate'
import { getInventoryByPlate } from '@/api/inventory'
import { useUserStore } from '@/stores/user'
import { formatDateTime } from '@/utils/format'

const userStore = useUserStore()

const loading = ref(false)
const submitLoading = ref(false)
const plateLoading = ref(false)
const tableData = ref<OutboundRecord[]>([])
const plateList = ref<Plate[]>([])
const total = ref(0)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentRecord = ref<OutboundRecord | null>(null)
const formRef = ref<FormInstance>()

const dateRange = ref<[string, string] | null>(null)

const queryParams = reactive<OutboundQuery>({
  page: 1,
  per_page: 10,
  plate_model: '',
  customer: '',
  status: ''
})

const formData = reactive({
  plate_id: 0,
  quantity: 1,
  customer: '',
  remark: ''
})

const formRules: FormRules = {
  plate_id: [{ required: true, message: '请选择铝板', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入出库数量', trigger: 'blur' }],
  customer: [{ required: true, message: '请输入客户名称', trigger: 'blur' }]
}

const availableStock = ref(0)

const fetchData = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_date = dateRange.value[0]
      queryParams.end_date = dateRange.value[1]
    }
    
    const res = await getOutboundList(queryParams)
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取出库记录失败:', error)
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

const handlePlateChange = async (plateId: number) => {
  if (!plateId) {
    availableStock.value = 0
    return
  }
  
  try {
    const res = await getInventoryByPlate(plateId)
    availableStock.value = res?.availableQuantity || 0
  } catch (error) {
    console.error('获取库存失败:', error)
    availableStock.value = 0
  }
}

const handleSearch = () => {
  queryParams.page = 1
  fetchData()
}

const handleReset = () => {
  dateRange.value = null
  queryParams.plate_model = ''
  queryParams.customer = ''
  queryParams.status = ''
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
  formData.customer = ''
  formData.remark = ''
  availableStock.value = 0
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  if (formData.quantity > availableStock.value) {
    ElMessage.warning('出库数量不能超过可用库存')
    return
  }
  
  submitLoading.value = true
  try {
    await createOutbound({
      plate_id: formData.plate_id,
      quantity: formData.quantity,
      customer: formData.customer,
      remark: formData.remark,
      applicant_name: userStore.userInfo?.real_name || '未知申请人'
    })
    ElMessage.success('出库申请已提交')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('出库申请失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleApprove = (row: OutboundRecord) => {
  ElMessageBox.confirm('确定要通过此出库申请吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await approveOutbound(row.id, {
        status: 'approved',
        reviewer_remark: ''
      })
      ElMessage.success('审批通过')
      fetchData()
    } catch (error) {
      console.error('审批失败:', error)
    }
  }).catch(() => {})
}

const handleReject = (row: OutboundRecord) => {
  ElMessageBox.prompt('请输入拒绝原因', '拒绝出库申请', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '请输入拒绝原因'
  }).then(async ({ value }) => {
    try {
      await rejectOutbound(row.id, {
        status: 'rejected',
        reviewer_remark: value
      })
      ElMessage.success('已拒绝')
      fetchData()
    } catch (error) {
      console.error('操作失败:', error)
    }
  }).catch(() => {})
}

const handleView = (row: OutboundRecord) => {
  currentRecord.value = row
  detailDialogVisible.value = true
}

const getStatusType = (status?: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status || ''] || 'info'
}

const getStatusText = (status?: string) => {
  const map: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status || ''] || status
}

onMounted(() => {
  fetchData()
  fetchPlateList()
})
</script>

<style scoped lang="scss">
.outbound-container {
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
    }
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
