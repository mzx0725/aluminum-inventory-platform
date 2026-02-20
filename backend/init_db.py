from app import db
from app.models import User, AluminumPlate, Inventory
from werkzeug.security import generate_password_hash

def init_database():
    """初始化数据库"""
    db.create_all()
    
    if User.query.first() is None:
        admin = User(
            username='admin',
            real_name='管理员',
            role='admin',
            status='active'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        warehouse = User(
            username='warehouse',
            real_name='仓库管理员',
            role='warehouse',
            status='active'
        )
        warehouse.set_password('123456')
        db.session.add(warehouse)
        
        dispatcher = User(
            username='dispatcher',
            real_name='调度员',
            role='dispatcher',
            status='active'
        )
        dispatcher.set_password('123456')
        db.session.add(dispatcher)
        
        db.session.commit()
        print('默认用户创建成功')
    
    print('数据库初始化完成')


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        init_database()