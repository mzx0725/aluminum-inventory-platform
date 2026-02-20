<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>调度任务</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>
      
      <div class="filter-section">
        <el-form :inline="true" :model="queryParams">
          <el-form-item label="关键词">
            <el-input
              v-model="queryParams.keyword"
              placeholder="搜索任务标题/描述"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
              style="width: 200px;"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="queryParams.status"
              placeholder="全部状态"
              clearable
              @change="handleSearch"
              style="width: 140px;"
            >
              <el-option label="待处理" value="pending" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select
              v-model="queryParams.priority"
              placeholder="全部优先级"
              clearable
              @change="handleSearch"
              style="width: 140px;"
            >
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="assignee" label="执行人" width="120">
          <template #default="{ row }">
            <span>{{ row.assignee || '未分配' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="120">
          <template #default="{ row }">
            <span>{{ row.due_date || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            <span>{{ formatDateTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleUpdateStatus(row)">
              更新状态
            </el-button>
            <el-button type="primary" link @click="handleAssign(row)">
              分配
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
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
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入任务标题" maxlength="100" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入任务描述"
            maxlength="500"
          />
        </el-form-item>
        <el-form-item label="执行人" prop="assignee_id">
          <el-select
            v-model="formData.assignee_id"
            placeholder="请选择执行人"
            clearable
            filterable
            style="width: 100%;"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级" style="width: 100%;">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker
            v-model="formData.due_date"
            type="date"
            placeholder="请选择截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="statusDialogVisible"
      title="更新任务状态"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="当前状态">
          <el-tag :type="currentTask?.status ? getStatusType(currentTask.status) : 'info'">
            {{ currentTask?.status ? getStatusText(currentTask.status) : '-' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="新状态">
          <el-select v-model="newStatus" placeholder="请选择新状态" style="width: 100%;">
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="statusLoading" @click="handleStatusSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="assignDialogVisible"
      title="分配任务"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="当前执行人">
          <span>{{ currentTask?.assignee || '未分配' }}</span>
        </el-form-item>
        <el-form-item label="新执行人">
          <el-select
            v-model="newAssigneeId"
            placeholder="请选择执行人"
            filterable
            style="width: 100%;"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="assignLoading" @click="handleAssignSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Task, TaskFormData, TaskQuery, TaskStatus } from '@/types/task'
import type { User } from '@/types/user'
import { getTaskList, createTask, updateTask, deleteTask, updateTaskStatus, assignTask } from '@/api/task'
import { get } from '@/utils/request'
import { formatDateTime } from '@/utils/format'

const queryParams = reactive<TaskQuery>({
  page: 1,
  page_size: 10,
  keyword: '',
  status: undefined,
  priority: undefined
})

const loading = ref(false)
const tableData = ref<Task[]>([])
const total = ref(0)
const userList = ref<User[]>([])

const dialogVisible = ref(false)
const dialogTitle = computed(() => isEdit.value ? '编辑任务' : '新建任务')
const isEdit = ref(false)
const currentTask = ref<Task | null>(null)
const submitLoading = ref(false)

const formRef = ref<FormInstance>()
const formData = reactive<TaskFormData>({
  title: '',
  description: '',
  assignee_id: null,
  priority: 'medium',
  due_date: null
})

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

const statusDialogVisible = ref(false)
const newStatus = ref<TaskStatus>('pending')
const statusLoading = ref(false)

const assignDialogVisible = ref(false)
const newAssigneeId = ref<number | null>(null)
const assignLoading = ref(false)

const fetchTaskList = async () => {
  loading.value = true
  try {
    const res = await getTaskList(queryParams)
    if (res) {
      tableData.value = res.list || []
      total.value = res.total || 0
    }
  } catch (error) {
    console.error('获取任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchUserList = async () => {
  try {
    const res = await get<{ list: User[] }>('/auth/users', { page: 1, per_page: 1000 })
    if (res && res.list) {
      userList.value = res.list
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const handleSearch = () => {
  queryParams.page = 1
  fetchTaskList()
}

const handleReset = () => {
  queryParams.keyword = ''
  queryParams.status = undefined
  queryParams.priority = undefined
  queryParams.page = 1
  fetchTaskList()
}

const handleSizeChange = (size: number) => {
  queryParams.page_size = size
  fetchTaskList()
}

const handleCurrentChange = (page: number) => {
  queryParams.page = page
  fetchTaskList()
}

const handleAdd = () => {
  isEdit.value = false
  currentTask.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Task) => {
  isEdit.value = true
  currentTask.value = row
  formData.title = row.title
  formData.description = row.description
  formData.assignee_id = row.assignee_id
  formData.priority = row.priority
  formData.due_date = row.due_date
  dialogVisible.value = true
}

const resetForm = () => {
  formData.title = ''
  formData.description = ''
  formData.assignee_id = null
  formData.priority = 'medium'
  formData.due_date = null
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value && currentTask.value) {
          await updateTask(currentTask.value.id, formData)
          ElMessage.success('更新成功')
        } else {
          await createTask(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchTaskList()
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: Task) => {
  ElMessageBox.confirm(`确定要删除任务 "${row.title}" 吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteTask(row.id)
      ElMessage.success('删除成功')
      fetchTaskList()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleUpdateStatus = (row: Task) => {
  currentTask.value = row
  newStatus.value = row.status
  statusDialogVisible.value = true
}

const handleStatusSubmit = async () => {
  if (!currentTask.value) return
  
  statusLoading.value = true
  try {
    await updateTaskStatus(currentTask.value.id, { status: newStatus.value })
    ElMessage.success('状态更新成功')
    statusDialogVisible.value = false
    fetchTaskList()
  } catch (error) {
    console.error('更新状态失败:', error)
  } finally {
    statusLoading.value = false
  }
}

const handleAssign = (row: Task) => {
  currentTask.value = row
  newAssigneeId.value = row.assignee_id
  assignDialogVisible.value = true
}

const handleAssignSubmit = async () => {
  if (!currentTask.value || !newAssigneeId.value) {
    ElMessage.warning('请选择执行人')
    return
  }
  
  assignLoading.value = true
  try {
    await assignTask(currentTask.value.id, { assignee_id: newAssigneeId.value })
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    fetchTaskList()
  } catch (error) {
    console.error('分配失败:', error)
  } finally {
    assignLoading.value = false
  }
}

const getStatusType = (status: TaskStatus) => {
  const map: Record<TaskStatus, string> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status: TaskStatus) => {
  const map: Record<TaskStatus, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
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

onMounted(() => {
  fetchTaskList()
  fetchUserList()
})
</script>

<style scoped lang="scss">
.tasks-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .filter-section {
    margin-bottom: 20px;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
