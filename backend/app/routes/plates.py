"""
铝板信息管理路由蓝图
"""
import jwt
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app import db
from app.models import AluminumPlate, User

plates_bp = Blueprint('plates', __name__)


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


def check_permission(user_role):
    """检查用户权限"""
    return user_role in ['admin', 'warehouse']


@plates_bp.route('', methods=['GET'])
def get_plates():
    """获取铝板列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)

    query = AluminumPlate.query

    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                AluminumPlate.model.ilike(search_pattern),
                AluminumPlate.specification.ilike(search_pattern),
                AluminumPlate.supplier.ilike(search_pattern)
            )
        )

    pagination = query.order_by(AluminumPlate.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'list': [plate.to_dict() for plate in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@plates_bp.route('/<int:plate_id>', methods=['GET'])
def get_plate(plate_id):
    """获取铝板详情"""
    plate = AluminumPlate.query.get(plate_id)

    if not plate:
        return jsonify({'error': '铝板信息不存在'}), 404

    return jsonify(plate.to_dict()), 200


@plates_bp.route('', methods=['POST'])
@token_required
def create_plate(current_user):
    """创建铝板信息"""
    if not check_permission(current_user.role):
        return jsonify({'error': '权限不足，只有仓库管理员或管理员才能创建铝板信息'}), 403

    data = request.get_json()

    if not data or not data.get('model') or not data.get('specification'):
        return jsonify({'error': '型号和规格不能为空'}), 400

    existing_plate = AluminumPlate.query.filter_by(
        model=data['model'],
        specification=data['specification']
    ).first()

    if existing_plate:
        return jsonify({'error': '该型号和规格的铝板已存在'}), 400

    plate = AluminumPlate(
        model=data['model'],
        specification=data['specification'],
        unit=data.get('unit', '张'),
        supplier=data.get('supplier'),
        remark=data.get('remark')
    )

    db.session.add(plate)
    db.session.commit()

    return jsonify(plate.to_dict()), 201


@plates_bp.route('/<int:plate_id>', methods=['PUT'])
@token_required
def update_plate(current_user, plate_id):
    """更新铝板信息"""
    if not check_permission(current_user.role):
        return jsonify({'error': '权限不足，只有仓库管理员或管理员才能更新铝板信息'}), 403

    plate = AluminumPlate.query.get(plate_id)

    if not plate:
        return jsonify({'error': '铝板信息不存在'}), 404

    data = request.get_json()

    if data.get('model'):
        plate.model = data['model']

    if data.get('specification'):
        plate.specification = data['specification']

    if data.get('unit'):
        plate.unit = data['unit']

    if 'supplier' in data:
        plate.supplier = data['supplier']

    if 'remark' in data:
        plate.remark = data['remark']

    if data.get('model') or data.get('specification'):
        existing_plate = AluminumPlate.query.filter(
            AluminumPlate.id != plate_id,
            AluminumPlate.model == plate.model,
            AluminumPlate.specification == plate.specification
        ).first()

        if existing_plate:
            return jsonify({'error': '该型号和规格的铝板已存在'}), 400

    db.session.commit()

    return jsonify(plate.to_dict()), 200


@plates_bp.route('/<int:plate_id>', methods=['DELETE'])
@token_required
def delete_plate(current_user, plate_id):
    """删除铝板信息"""
    if not check_permission(current_user.role):
        return jsonify({'error': '权限不足，只有仓库管理员或管理员才能删除铝板信息'}), 403

    plate = AluminumPlate.query.get(plate_id)

    if not plate:
        return jsonify({'error': '铝板信息不存在'}), 404

    if plate.inventories.count() > 0:
        return jsonify({'error': '该铝板存在库存记录，无法删除'}), 400

    if plate.inbound_records.count() > 0:
        return jsonify({'error': '该铝板存在入库记录，无法删除'}), 400

    if plate.outbound_records.count() > 0:
        return jsonify({'error': '该铝板存在出库记录，无法删除'}), 400

    db.session.delete(plate)
    db.session.commit()

    return jsonify({'message': '删除成功'}), 200