<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
            </div>
          </template>
          
          <div class="avatar-section">
            <el-avatar :size="100" class="user-avatar">
              {{ userStore.userInfo?.real_name?.charAt(0) || 'U' }}
            </el-avatar>
            <h3 class="user-name">{{ userStore.userInfo?.real_name || '用户' }}</h3>
            <el-tag :type="getRoleType(userStore.userInfo?.role)">
              {{ getRoleText(userStore.userInfo?.role) }}
            </el-tag>
          </div>
          
          <el-descriptions :column="1" border class="info-descriptions">
            <el-descriptions-item label="用户名">
              {{ userStore.userInfo?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="真实姓名">
              {{ userStore.userInfo?.real_name }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              {{ getRoleText(userStore.userInfo?.role) }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="userStore.userInfo?.status === 'active' ? 'success' : 'danger'" size="small">
                {{ userStore.userInfo?.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(userStore.userInfo?.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>修改信息</span>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="info">
              <el-form
                ref="infoFormRef"
                :model="infoForm"
                :rules="infoRules"
                label-width="100px"
                class="form-section"
              >
                <el-form-item label="真实姓名" prop="real_name">
                  <el-input v-model="infoForm.real_name" placeholder="请输入真实姓名" />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" :loading="infoLoading" @click="handleUpdateInfo">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="修改密码" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="100px"
                class="form-section"
              >
                <el-form-item label="当前密码" prop="oldPassword">
                  <el-input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="passwordForm.newPassword"
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" :loading="passwordLoading" @click="handleUpdatePassword">
                    修改密码
                  </el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { put } from '@/utils/request'
import { formatDateTime } from '@/utils/format'

const userStore = useUserStore()

const activeTab = ref('info')
const infoFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const infoLoading = ref(false)
const passwordLoading = ref(false)

const infoForm = reactive({
  real_name: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const infoRules: FormRules = {
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const getRoleType = (role?: string) => {
  const types: Record<string, string> = {
    admin: 'danger',
    warehouse: 'warning',
    dispatcher: 'primary'
  }
  return types[role || ''] || 'info'
}

const getRoleText = (role?: string) => {
  const texts: Record<string, string> = {
    admin: '管理员',
    warehouse: '仓库管理员',
    dispatcher: '调度员'
  }
  return texts[role || ''] || role
}

const handleUpdateInfo = async () => {
  if (!infoFormRef.value) return
  
  await infoFormRef.value.validate(async (valid) => {
    if (valid) {
      infoLoading.value = true
      try {
        await put(`/users/${userStore.userInfo?.id}`, infoForm)
        userStore.userInfo!.real_name = infoForm.real_name
        ElMessage.success('修改成功')
      } catch (error: any) {
        ElMessage.error(error.message || '修改失败')
      } finally {
        infoLoading.value = false
      }
    }
  })
}

const handleUpdatePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        await put(`/users/${userStore.userInfo?.id}/password`, {
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        })
        ElMessage.success('密码修改成功')
        resetPasswordForm()
      } catch (error: any) {
        ElMessage.error(error.message || '密码修改失败')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordFormRef.value?.resetFields()
}

onMounted(() => {
  if (userStore.userInfo) {
    infoForm.real_name = userStore.userInfo.real_name
  }
})
</script>

<style scoped lang="scss">
.profile-page {
  padding: 0;
}

.profile-card {
  .card-header {
    font-size: 16px;
    font-weight: 500;
  }
  
  .avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
    
    .user-avatar {
      background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
      color: #fff;
      font-size: 36px;
    }
    
    .user-name {
      margin: 16px 0 8px;
      font-size: 18px;
      color: var(--text-color-primary);
    }
  }
  
  .info-descriptions {
    margin-top: 20px;
  }
}

.form-section {
  max-width: 500px;
  padding: 20px 0;
}
</style>
