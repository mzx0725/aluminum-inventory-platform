"""
认证路由蓝图
"""
import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


def generate_token(user_id):
    """生成JWT Token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


def token_required(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token格式错误'}), 401
        
        if not token:
            return jsonify({'error': '缺少Token'}), 401
        
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的Token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if user.status != 'active':
        return jsonify({'error': '账户已被禁用'}), 403
    
    token = generate_token(user.id)
    
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'expiresIn': 7 * 24 * 60 * 60
    }), 200


@auth_bp.route('/userinfo', methods=['GET'])
@token_required
def get_userinfo(current_user):
    """获取当前用户信息"""
    return jsonify(current_user.to_dict()), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({'message': '登出成功'}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('real_name'):
        return jsonify({'error': '用户名、密码和真实姓名不能为空'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    user = User(
        username=data['username'],
        real_name=data['real_name'],
        role=data.get('role', 'warehouse'),
        status=data.get('status', 'active')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    username = request.args.get('username', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    
    query = User.query
    
    if username:
        query = query.filter(User.username.ilike(f'%{username}%'))
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'list': [user.to_dict() for user in pagination.items],
        'total': pagination.total
    }), 200


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """获取用户详情"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """更新用户信息"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    if data.get('real_name'):
        user.real_name = data['real_name']
    
    if data.get('role'):
        user.role = data['role']
    
    if data.get('status'):
        user.status = data['status']
    
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': '更新成功',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """删除用户"""
    from app.models import InboundRecord, OutboundRecord, DispatchTask
    
    if current_user.id == user_id:
        return jsonify({'error': '不能删除自己的账户'}), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    if user.username == 'admin':
        return jsonify({'error': '不能删除管理员账户'}), 400
    
    inbound_count = InboundRecord.query.filter_by(operator_id=user_id).count()
    outbound_count = OutboundRecord.query.filter_by(applicant_id=user_id).count()
    task_count = DispatchTask.query.filter(
        (DispatchTask.assignee_id == user_id) | (DispatchTask.creator_id == user_id)
    ).count()
    
    if inbound_count > 0 or outbound_count > 0 or task_count > 0:
        return jsonify({
            'error': f'无法删除该用户，存在关联数据：入库记录 {inbound_count} 条、出库记录 {outbound_count} 条、任务 {task_count} 条。请先处理相关数据或禁用该账户。'
        }), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200


@auth_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@token_required
def reset_password(current_user, user_id):
    """重置用户密码"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    import random
    import string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'password': new_password}), 200


@auth_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@token_required
def update_user_status(current_user, user_id):
    """更新用户状态"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['active', 'inactive', 'disabled']:
        return jsonify({'error': '无效的状态'}), 400
    
    user.status = status
    db.session.commit()
    
    return jsonify(user.to_dict()), 200