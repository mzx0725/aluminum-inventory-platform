<template>
  <div class="inventory-container">
    <el-card class="search-card">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="铝板型号">
          <el-input v-model="queryParams.plateCode" placeholder="请输入铝板型号" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="存放位置">
          <el-input v-model="queryParams.location" placeholder="请输入存放位置" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="queryParams.batchNumber" placeholder="请输入批次号" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="queryParams.low_stock" @change="handleSearch">仅显示低库存</el-checkbox>
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
          <span>库存列表</span>
          <el-button type="primary" @click="handleCheck">
            <el-icon><Check /></el-icon>
            库存盘点
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="plateCode" label="铝板型号" width="150" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="material" label="材质" width="100" />
        <el-table-column prop="totalQuantity" label="总数量" width="100">
          <template #default="{ row }">
            <el-tag :type="row.totalQuantity <= 10 ? 'danger' : 'success'">{{ row.totalQuantity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="availableQuantity" label="可用数量" width="100" />
        <el-table-column prop="location" label="存放位置" width="120" />
        <el-table-column prop="batchNumber" label="批次号" width="150" />
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column prop="updatedAt" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewCheck(row)">盘点</el-button>
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

    <CheckDialog
      v-model="checkDialogVisible"
      :inventory-item="selectedInventory"
      @success="handleCheckSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Check } from '@element-plus/icons-vue'
import { getInventoryList, type InventoryItem } from '@/api/inventory'
import type { InventoryQuery } from '@/types/inventory'
import { formatDateTime } from '@/utils/format'
import CheckDialog from './components/CheckDialog.vue'

const loading = ref(false)
const tableData = ref<InventoryItem[]>([])
const total = ref(0)
const checkDialogVisible = ref(false)
const selectedInventory = ref<InventoryItem | null>(null)

const queryParams = reactive<InventoryQuery>({
  page: 1,
  per_page: 10,
  plateCode: '',
  location: '',
  batchNumber: '',
  low_stock: false
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getInventoryList(queryParams)
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取库存列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  fetchData()
}

const handleReset = () => {
  queryParams.plateCode = ''
  queryParams.location = ''
  queryParams.batchNumber = ''
  queryParams.low_stock = false
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

const handleCheck = () => {
  selectedInventory.value = null
  checkDialogVisible.value = true
}

const handleViewCheck = (row: InventoryItem) => {
  selectedInventory.value = row
  checkDialogVisible.value = true
}

const handleCheckSuccess = () => {
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.inventory-container {
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
