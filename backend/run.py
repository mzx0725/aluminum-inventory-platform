"""
Flask应用入口文件
"""
import os
from app import create_app

# 从环境变量获取配置名称，默认为development
config_name = os.getenv('FLASK_ENV', 'development')

# 创建Flask应用实例
app = create_app(config_name)


@app.route('/')
def index():
    """根路径健康检查"""
    return {
        'message': '铝板库存管理系统 API',
        'status': 'running',
        'version': '1.0.0'
    }


@app.route('/api/health')
def health():
    """健康检查接口"""
    return {
        'status': 'healthy',
        'database': 'connected'
    }


if __name__ == '__main__':
    # 开发环境运行配置
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
