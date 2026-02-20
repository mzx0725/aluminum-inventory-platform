<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>
      
      <el-form :model="queryParams" inline class="search-form">
        <el-form-item label="用户名">
          <el-input 
            v-model="queryParams.username" 
            placeholder="请输入用户名" 
            clearable 
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="queryParams.role" placeholder="请选择角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="仓库管理员" value="warehouse" />
            <el-option label="调度员" value="dispatcher" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table 
        v-loading="loading" 
        :data="tableData" 
        border 
        stripe
      >
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="inactive"
              :loading="row.statusLoading"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleResetPassword(row)">重置密码</el-button>
            <el-button 
              type="danger" 
              link 
              :disabled="row.username === 'admin'"
              @click="handleDelete(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.per_page"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchUserList"
        @current-change="fetchUserList"
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="formData.username" 
            placeholder="请输入用户名"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="formData.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="仓库管理员" value="warehouse" />
            <el-option label="调度员" value="dispatcher" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input 
            v-model="formData.password" 
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  getUserListApi, 
  createUserApi, 
  updateUserApi, 
  deleteUserApi, 
  resetPasswordApi,
  updateUserStatusApi 
} from '@/api/user'
import type { User, UserQuery, UserFormData, UserRole } from '@/types/user'
import { formatDateTime } from '@/utils/format'

const queryParams = reactive<UserQuery>({
  page: 1,
  per_page: 10,
  username: '',
  role: undefined,
  status: undefined
})

const loading = ref(false)
const total = ref(0)
const tableData = ref<User[]>([])

const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const currentUserId = ref<number | null>(null)

const formData = reactive<UserFormData>({
  username: '',
  real_name: '',
  role: 'warehouse',
  password: '',
  status: 'active'
})

const dialogTitle = computed(() => isEdit.value ? '编辑用户' : '新增用户')

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '真实姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

const getRoleType = (role: UserRole) => {
  const types: Record<UserRole, string> = {
    admin: 'danger',
    warehouse: 'warning',
    dispatcher: 'primary'
  }
  return types[role] || 'info'
}

const getRoleText = (role: UserRole) => {
  const texts: Record<UserRole, string> = {
    admin: '管理员',
    warehouse: '仓库管理员',
    dispatcher: '调度员'
  }
  return texts[role] || role
}

const fetchUserList = async () => {
  loading.value = true
  try {
    const response = await getUserListApi(queryParams)
    tableData.value = response.list
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  fetchUserList()
}

const handleReset = () => {
  queryParams.username = ''
  queryParams.role = undefined
  queryParams.status = undefined
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  currentUserId.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: User) => {
  isEdit.value = true
  currentUserId.value = row.id
  Object.assign(formData, {
    username: row.username,
    real_name: row.real_name,
    role: row.role,
    status: row.status,
    password: ''
  })
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(formData, {
    username: '',
    real_name: '',
    role: 'warehouse',
    password: '',
    status: 'active'
  })
  formRef.value?.resetFields()
}

const handleDialogClosed = () => {
  resetForm()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value && currentUserId.value) {
          const updateData: Partial<UserFormData> = {
            real_name: formData.real_name,
            role: formData.role,
            status: formData.status
          }
          await updateUserApi(currentUserId.value, updateData)
          ElMessage.success('更新成功')
        } else {
          await createUserApi(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchUserList()
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: User) => {
  if (row.username === 'admin') {
    ElMessage.warning('不能删除管理员账号')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除用户 "${row.username}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteUserApi(row.id)
      ElMessage.success('删除成功')
      fetchUserList()
    } catch (error: any) {
      ElMessage.error(error.message || '删除失败')
    }
  }).catch(() => {})
}

const handleResetPassword = (row: User) => {
  ElMessageBox.confirm(
    `确定要重置用户 "${row.username}" 的密码吗？密码将被重置为默认密码。`,
    '重置密码',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await resetPasswordApi(row.id)
      ElMessage.success(`密码已重置为: ${response.password}`)
    } catch (error: any) {
      ElMessage.error(error.message || '重置密码失败')
    }
  }).catch(() => {})
}

const handleStatusChange = async (row: User & { statusLoading?: boolean }) => {
  row.statusLoading = true
  try {
    await updateUserStatusApi(row.id, row.status)
    ElMessage.success(`${row.username} 已${row.status === 'active' ? '启用' : '禁用'}`)
  } catch (error: any) {
    row.status = row.status === 'active' ? 'inactive' : 'active'
    ElMessage.error(error.message || '状态更新失败')
  } finally {
    row.statusLoading = false
  }
}

onMounted(() => {
  fetchUserList()
})
</script>

<style scoped lang="scss">
.users-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .search-form {
    margin-bottom: 16px;
  }
  
  .pagination {
    margin-top: 16px;
    justify-content: flex-end;
  }
}
</style>
