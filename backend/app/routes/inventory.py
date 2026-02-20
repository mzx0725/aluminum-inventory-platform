"""
库存管理路由蓝图
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Inventory, InventoryCheck, AluminumPlate

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('', methods=['GET'])
def get_inventories():
    """
    获取库存列表
    支持分页、搜索、筛选低库存
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    low_stock = request.args.get('low_stock', '').lower() == 'true'

    query = Inventory.query.join(AluminumPlate)

    if search:
        query = query.filter(
            db.or_(
                AluminumPlate.model.contains(search),
                AluminumPlate.specification.contains(search),
                Inventory.batch_number.contains(search)
            )
        )

    if low_stock:
        query = query.filter(Inventory.quantity <= Inventory.warning_threshold)

    pagination = query.order_by(Inventory.last_updated.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'list': [inventory.to_dict() for inventory in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    """获取库存详情"""
    inventory = Inventory.query.get(inventory_id)

    if not inventory:
        return jsonify({'error': '库存记录不存在'}), 404

    return jsonify({'inventory': inventory.to_dict()}), 200


@inventory_bp.route('/warnings', methods=['GET'])
def get_inventory_warnings():
    """获取库存预警列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Inventory.query.filter(
        Inventory.quantity <= Inventory.warning_threshold
    ).join(AluminumPlate)

    pagination = query.order_by(Inventory.quantity.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'warnings': [inventory.to_dict() for inventory in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@inventory_bp.route('/check', methods=['POST'])
def create_inventory_check():
    """创建盘点记录"""
    data = request.get_json()

    if not data or not data.get('inventory_id') or data.get('actual_quantity') is None:
        return jsonify({'error': '库存ID和实际数量不能为空'}), 400

    inventory = Inventory.query.get(data['inventory_id'])
    if not inventory:
        return jsonify({'error': '库存记录不存在'}), 404

    actual_quantity = int(data['actual_quantity'])
    expected_quantity = inventory.quantity
    difference = actual_quantity - expected_quantity

    from app.models import User
    checker = User.query.first()

    check = InventoryCheck(
        inventory_id=data['inventory_id'],
        expected_quantity=expected_quantity,
        actual_quantity=actual_quantity,
        difference=difference,
        checker_id=checker.id if checker else 1,
        remark=data.get('remark')
    )

    db.session.add(check)
    inventory.quantity = actual_quantity

    db.session.commit()

    return jsonify({
        'message': '盘点记录创建成功',
        'check': check.to_dict()
    }), 201


@inventory_bp.route('/checks', methods=['GET'])
def get_inventory_checks():
    """获取盘点记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    inventory_id = request.args.get('inventory_id', type=int)
    checker_id = request.args.get('checker_id', type=int)

    query = InventoryCheck.query

    if inventory_id:
        query = query.filter_by(inventory_id=inventory_id)

    if checker_id:
        query = query.filter_by(checker_id=checker_id)

    pagination = query.order_by(InventoryCheck.check_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'checks': [check.to_dict() for check in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200