# 铝板智慧物料管控平台

一个基于 Vue 3 + Flask 的铝板出入库调度运维管理系统。

## 功能特性

- **用户管理**: 用户登录、权限控制、用户增删改查
- **铝板信息管理**: 铝板型号、规格、供应商管理
- **入库管理**: 入库登记、入库记录查询、导出 Excel
- **出库管理**: 出库申请、审批流程、出库记录
- **库存管理**: 实时库存查看、盘点、预警功能
- **调度任务**: 任务创建、分配、状态跟踪
- **统计分析**: 数据可视化、报表生成

## 技术栈

### 前端
- Vue 3 + TypeScript
- Element Plus UI
- Vite
- Pinia 状态管理
- ECharts 图表

### 后端
- Python 3.8+
- Flask
- SQLAlchemy
- SQLite

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+

### 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 启动服务

**方式一：使用启动脚本**
```bash
# Windows
双击运行 启动平台.bat
```

**方式二：手动启动**
```bash
# 启动后端 (端口 5000)
cd backend
python run.py

# 启动前端 (端口 3000)
cd frontend
npm run dev
```

### 访问系统

- 前端地址: http://localhost:3000
- 后端地址: http://127.0.0.1:5000
- 默认账号: admin
- 默认密码: admin123

## 项目结构

```
software-copyright/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── models.py       # 数据模型
│   │   ├── routes/         # API 路由
│   │   └── utils/          # 工具函数
│   ├── config.py           # 配置文件
│   ├── init_db.py          # 数据库初始化
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API 接口
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # 状态管理
│   │   └── router/         # 路由配置
│   └── package.json        # Node 依赖
├── screenshot-tool/        # 截图工具
├── supabase/               # Supabase 配置
├── 启动平台.bat            # 启动脚本
└── 停止平台.bat            # 停止脚本
```

## 许可证

MIT License
