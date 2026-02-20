"""
数据库初始化脚本
创建数据库表并添加默认管理员账户
"""
from app import create_app, db
from app.models import User


def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        # 删除所有表（开发环境）
        print('正在删除旧数据库表...')
        db.drop_all()
        
        # 创建所有表
        print('正在创建数据库表...')
        db.create_all()
        
        # 创建默认管理员账户
        print('正在创建默认管理员账户...')
        admin = User(
            username='admin',
            real_name='系统管理员',
            role='admin',
            status='active'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        
        # 创建测试用户
        print('正在创建测试用户...')
        warehouse_user = User(
            username='warehouse',
            real_name='仓库管理员',
            role='warehouse',
            status='active'
        )
        warehouse_user.set_password('warehouse123')
        
        dispatcher_user = User(
            username='dispatcher',
            real_name='调度员',
            role='dispatcher',
            status='active'
        )
        dispatcher_user.set_password('dispatcher123')
        
        db.session.add(warehouse_user)
        db.session.add(dispatcher_user)
        
        # 提交事务
        db.session.commit()
        
        print('数据库初始化完成！')
        print('\n默认账户信息：')
        print('管理员 - 用户名: admin, 密码: admin123')
        print('仓库管理员 - 用户名: warehouse, 密码: warehouse123')
        print('调度员 - 用户名: dispatcher, 密码: dispatcher123')
        print('\n数据库文件位置: backend/app.db')


if __name__ == '__main__':
    init_database()