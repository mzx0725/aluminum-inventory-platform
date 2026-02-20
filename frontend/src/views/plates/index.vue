<template>
  <div class="plates-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>铝板管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增铝板
          </el-button>
        </div>
      </template>
      
      <el-form :model="queryParams" inline class="search-form">
        <el-form-item label="搜索">
          <el-input v-model="queryParams.search" placeholder="型号/规格/供应商" clearable style="width: 200px" />
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
      
      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="specification" label="规格" width="150" />
        <el-table-column prop="unit" label="单位" width="80">
          <template #default="{ row }">
            {{ row.unit || '张' }}
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="型号" prop="model">
          <el-input v-model="formData.model" placeholder="请输入型号，如 AL-6061" />
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="formData.specification" placeholder="请输入规格，如 1000x500x2mm" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="formData.unit" placeholder="请选择单位" style="width: 100%">
            <el-option label="张" value="张" />
            <el-option label="块" value="块" />
            <el-option label="根" value="根" />
            <el-option label="公斤" value="公斤" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="formData.supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { getPlateList, createPlate, updatePlate, deletePlate, type Plate, type PlateQuery, type PlateFormData } from '@/api/plate'

const queryParams = reactive<PlateQuery>({
  page: 1,
  per_page: 10,
  search: ''
})

const loading = ref(false)
const total = ref(0)
const tableData = ref<Plate[]>([])

const dialogVisible = ref(false)
const dialogTitle = computed(() => formData.id ? '编辑铝板' : '新增铝板')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const formData = reactive<PlateFormData & { id?: number }>({
  model: '',
  specification: '',
  unit: '张',
  supplier: '',
  remark: ''
})

const formRules: FormRules = {
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  specification: [{ required: true, message: '请输入规格', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择单位', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getPlateList(queryParams)
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  loadData()
}

const handleReset = () => {
  queryParams.search = ''
  handleSearch()
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Plate) => {
  resetForm()
  Object.assign(formData, {
    id: row.id,
    model: row.model,
    specification: row.specification,
    unit: row.unit || '张',
    supplier: row.supplier,
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

const handleDelete = (row: Plate) => {
  ElMessageBox.confirm(`确定要删除铝板「${row.model}」吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deletePlate(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitLoading.value = true
  try {
    const data: PlateFormData = {
      model: formData.model,
      specification: formData.specification,
      unit: formData.unit,
      supplier: formData.supplier,
      remark: formData.remark
    }
    
    if (formData.id) {
      await updatePlate(formData.id, data)
      ElMessage.success('更新成功')
    } else {
      await createPlate(data)
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    id: undefined,
    model: '',
    specification: '',
    unit: '张',
    supplier: '',
    remark: ''
  })
  formRef.value?.resetFields()
}

const handleSizeChange = (size: number) => {
  queryParams.per_page = size
  loadData()
}

const handleCurrentChange = (page: number) => {
  queryParams.page = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.plates-container {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .search-form {
    margin-bottom: 16px;
  }
  
  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
