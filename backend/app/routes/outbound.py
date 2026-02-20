"""
出库管理路由蓝图
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import and_
from app import db
from app.models import OutboundRecord, Inventory, User, DispatchTask, AluminumPlate
from app.utils.time_utils import get_beijing_time

outbound_bp = Blueprint('outbound', __name__)


@outbound_bp.route('', methods=['POST'])
def create_outbound():
    """创建出库申请"""
    data = request.get_json()
    
    if not data or not data.get('plate_id') or not data.get('quantity'):
        return jsonify({'error': '铝板ID和数量不能为空'}), 400
    
    plate_id = data['plate_id']
    quantity = data['quantity']
    applicant_id = data.get('applicant_id')
    applicant_name = data.get('applicant_name', '未知用户')
    
    if quantity <= 0:
        return jsonify({'error': '出库数量必须大于0'}), 400
    
    if applicant_id:
        try:
            applicant_id = int(applicant_id)
            applicant = User.query.get(applicant_id)
        except (ValueError, TypeError):
            applicant = User.query.filter(
                db.or_(User.real_name == applicant_name, User.username == applicant_name)
            ).first()
    else:
        applicant = User.query.filter(
            db.or_(User.real_name == applicant_name, User.username == applicant_name)
        ).first()
    
    if not applicant:
        applicant = User.query.first()
    
    inventory = Inventory.query.filter_by(plate_id=plate_id).first()
    if not inventory:
        return jsonify({'error': '该铝板库存不存在'}), 404
    
    if inventory.quantity < quantity:
        return jsonify({'error': f'库存不足，当前库存: {inventory.quantity}'}), 400
    
    plate = AluminumPlate.query.get(plate_id)
    plate_info = f"{plate.model} - {plate.specification}" if plate else f"铝板ID:{plate_id}"
    
    outbound = OutboundRecord(
        plate_id=plate_id,
        quantity=quantity,
        applicant_id=applicant.id if applicant else 1,
        status='pending',
        remark=data.get('remark')
    )
    
    db.session.add(outbound)
    db.session.flush()
    
    admin_user = User.query.filter_by(role='admin').first()
    
    task = DispatchTask(
        title=f'出库审批: {plate_info} x {quantity}',
        description=f'申请人: {applicant_name}\n铝板: {plate_info}\n数量: {quantity}\n备注: {data.get("remark", "无")}',
        assignee_id=admin_user.id if admin_user else 1,
        creator_id=applicant.id if applicant else 1,
        status='pending',
        priority='high',
        due_date=None
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': '出库申请创建成功',
        'outbound': outbound.to_dict()
    }), 201


@outbound_bp.route('', methods=['GET'])
def get_outbounds():
    """获取出库记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    plate_id = request.args.get('plate_id', type=int)
    applicant_id = request.args.get('applicant_id', type=int)
    
    query = OutboundRecord.query
    
    if status:
        query = query.filter(OutboundRecord.status == status)
    
    if plate_id:
        query = query.filter(OutboundRecord.plate_id == plate_id)
    
    if applicant_id:
        query = query.filter(OutboundRecord.applicant_id == applicant_id)
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(OutboundRecord.outbound_time >= start_datetime)
        except ValueError:
            return jsonify({'error': '开始日期格式错误'}), 400
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            query = query.filter(OutboundRecord.outbound_time <= end_datetime)
        except ValueError:
            return jsonify({'error': '结束日期格式错误'}), 400
    
    query = query.order_by(OutboundRecord.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'outbounds': [outbound.to_dict() for outbound in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@outbound_bp.route('/<int:outbound_id>', methods=['GET'])
def get_outbound(outbound_id):
    """获取出库记录详情"""
    outbound = OutboundRecord.query.get(outbound_id)
    
    if not outbound:
        return jsonify({'error': '出库记录不存在'}), 404
    
    return jsonify({'outbound': outbound.to_dict()}), 200


@outbound_bp.route('/<int:outbound_id>/approve', methods=['PUT'])
def approve_outbound(outbound_id):
    """审核通过出库申请"""
    data = request.get_json()
    
    approver_id = data.get('approver_id') if data else None
    
    if approver_id:
        try:
            approver_id = int(approver_id)
            approver = User.query.get(approver_id)
        except (ValueError, TypeError):
            approver = User.query.filter_by(role='admin').first()
    else:
        approver = User.query.filter_by(role='admin').first()
    
    outbound = OutboundRecord.query.get(outbound_id)
    if not outbound:
        return jsonify({'error': '出库记录不存在'}), 404
    
    if outbound.status != 'pending':
        return jsonify({'error': f'该出库申请已处理，当前状态: {outbound.status}'}), 400
    
    inventory = Inventory.query.filter_by(plate_id=outbound.plate_id).first()
    if not inventory:
        return jsonify({'error': '该铝板库存不存在'}), 404
    
    if inventory.quantity < outbound.quantity:
        return jsonify({'error': f'库存不足，当前库存: {inventory.quantity}'}), 400
    
    outbound.status = 'approved'
    outbound.approver_id = approver.id if approver else 1
    outbound.outbound_time = get_beijing_time()
    
    inventory.quantity -= outbound.quantity
    inventory.last_updated = get_beijing_time()
    
    db.session.commit()
    
    return jsonify({
        'message': '出库申请审核通过',
        'outbound': outbound.to_dict(),
        'inventory': inventory.to_dict()
    }), 200


@outbound_bp.route('/<int:outbound_id>/reject', methods=['PUT'])
def reject_outbound(outbound_id):
    """审核拒绝出库申请"""
    data = request.get_json()
    
    approver_id = data.get('approver_id') if data else None
    
    if approver_id:
        try:
            approver_id = int(approver_id)
            approver = User.query.get(approver_id)
        except (ValueError, TypeError):
            approver = User.query.filter_by(role='admin').first()
    else:
        approver = User.query.filter_by(role='admin').first()
    
    outbound = OutboundRecord.query.get(outbound_id)
    if not outbound:
        return jsonify({'error': '出库记录不存在'}), 404
    
    if outbound.status != 'pending':
        return jsonify({'error': f'该出库申请已处理，当前状态: {outbound.status}'}), 400
    
    outbound.status = 'rejected'
    outbound.approver_id = approver.id if approver else 1
    
    if data and data.get('reason'):
        if outbound.remark:
            outbound.remark += f'\n拒绝原因: {data["reason"]}'
        else:
            outbound.remark = f'拒绝原因: {data["reason"]}'
    
    db.session.commit()
    
    return jsonify({
        'message': '出库申请已拒绝',
        'outbound': outbound.to_dict()
    }), 200