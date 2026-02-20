"""
Flask应用初始化
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

db = SQLAlchemy()


def create_app(config_name='default'):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称 (development/production/testing)
    
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.plates import plates_bp
    from app.routes.inventory import inventory_bp
    from app.routes.inbound import inbound_bp
    from app.routes.outbound import outbound_bp
    from app.routes.tasks import tasks_bp
    from app.routes.statistics import statistics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(plates_bp, url_prefix='/api/plates')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(inbound_bp, url_prefix='/api/inbound')
    app.register_blueprint(outbound_bp, url_prefix='/api/outbound')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
