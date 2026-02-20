<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="库存盘点"
    width="500px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="库存项" prop="inventory_id">
        <el-select
          v-model="formData.inventory_id"
          placeholder="请选择库存项"
          filterable
          style="width: 100%"
          :disabled="!!inventoryItem"
          @change="handleInventoryChange"
        >
          <el-option
            v-for="item in inventoryList"
            :key="item.id"
            :label="`${item.plateCode} - ${item.specification}`"
            :value="item.id"
          >
            <div style="display: flex; justify-content: space-between;">
              <span>{{ item.plateCode }}</span>
              <span style="color: var(--el-text-color-secondary);">{{ item.specification }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <div v-if="selectedInventory" class="inventory-info">
        <el-descriptions :column="2" size="small" border>
          <el-descriptions-item label="铝板型号">{{ selectedInventory.plateCode }}</el-descriptions-item>
          <el-descriptions-item label="规格">{{ selectedInventory.specification }}</el-descriptions-item>
          <el-descriptions-item label="存放位置">{{ selectedInventory.location }}</el-descriptions-item>
          <el-descriptions-item label="批次号">{{ selectedInventory.batchNumber }}</el-descriptions-item>
          <el-descriptions-item label="系统数量">
            <el-tag type="info">{{ selectedInventory.totalQuantity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="可用数量">
            <el-tag :type="selectedInventory.availableQuantity > 0 ? 'success' : 'danger'">
              {{ selectedInventory.availableQuantity }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <el-form-item label="实际数量" prop="actual_quantity">
        <el-input-number
          v-model="formData.actual_quantity"
          :min="0"
          :precision="0"
          style="width: 100%"
          placeholder="请输入实际盘点数量"
        />
      </el-form-item>
      
      <div v-if="showDifference" class="difference-info">
        <el-alert
          :type="differenceType"
          :closable="false"
          show-icon
        >
          <template #title>
            <span>盘点差异：{{ difference > 0 ? '+' : '' }}{{ difference }}</span>
          </template>
          <div v-if="difference !== 0">
            {{ difference > 0 ? '盘盈：实际数量大于系统数量' : '盘亏：实际数量小于系统数量' }}
          </div>
        </el-alert>
      </div>
      
      <el-form-item label="备注" prop="remark">
        <el-input
          v-model="formData.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入盘点备注（选填）"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
        确认盘点
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { checkInventory, getInventoryList } from '@/api/inventory'
import type { InventoryItem } from '@/api/inventory'

const props = defineProps<{
  modelValue: boolean
  inventoryItem: InventoryItem | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref<FormInstance>()
const submitLoading = ref(false)
const inventoryList = ref<InventoryItem[]>([])

const formData = ref({
  inventory_id: 0,
  actual_quantity: 0,
  remark: ''
})

const formRules: FormRules = {
  inventory_id: [
    { required: true, message: '请选择库存项', trigger: 'change' }
  ],
  actual_quantity: [
    { required: true, message: '请输入实际数量', trigger: 'blur' },
    { type: 'number', min: 0, message: '数量不能为负数', trigger: 'blur' }
  ]
}

const selectedInventory = computed(() => {
  if (props.inventoryItem) {
    return props.inventoryItem
  }
  return inventoryList.value.find(item => item.id === formData.value.inventory_id) || null
})

const showDifference = computed(() => {
  return selectedInventory.value && formData.value.actual_quantity >= 0
})

const difference = computed(() => {
  if (!selectedInventory.value) return 0
  return formData.value.actual_quantity - selectedInventory.value.totalQuantity
})

const differenceType = computed(() => {
  if (difference.value === 0) return 'success'
  if (difference.value > 0) return 'warning'
  return 'error'
})

const loadInventoryList = async () => {
  try {
    const res = await getInventoryList({ per_page: 1000 })
    inventoryList.value = res.list || []
  } catch (error) {
    console.error('加载库存列表失败:', error)
  }
}

const handleInventoryChange = () => {
  if (selectedInventory.value) {
    formData.value.actual_quantity = selectedInventory.value.totalQuantity
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    try {
      await checkInventory({
        inventory_id: formData.value.inventory_id,
        actual_quantity: formData.value.actual_quantity,
        remark: formData.value.remark
      })
      
      ElMessage.success('盘点成功')
      emit('update:modelValue', false)
      emit('success')
    } catch (error) {
      console.error('盘点失败:', error)
    } finally {
      submitLoading.value = false
    }
  })
}

const handleClosed = () => {
  formData.value = {
    inventory_id: 0,
    actual_quantity: 0,
    remark: ''
  }
  formRef.value?.resetFields()
}

watch(() => props.modelValue, (val) => {
  if (val) {
    if (props.inventoryItem) {
      formData.value.inventory_id = props.inventoryItem.id
      formData.value.actual_quantity = props.inventoryItem.totalQuantity
    } else {
      loadInventoryList()
    }
  }
})
</script>

<style scoped lang="scss">
.inventory-info {
  margin-bottom: 20px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.difference-info {
  margin-bottom: 20px;
}
</style>
