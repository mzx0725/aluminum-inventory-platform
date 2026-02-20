"""
调度任务路由蓝图
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import DispatchTask, User
from app.utils.time_utils import get_beijing_time

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['POST'])
def create_task():
    """创建调度任务"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('assignee_id') or not data.get('creator_id'):
        return jsonify({'error': '任务标题、执行人和创建人不能为空'}), 400
    
    assignee = User.query.get(data['assignee_id'])
    if not assignee:
        return jsonify({'error': '执行人不存在'}), 404
    
    creator = User.query.get(data['creator_id'])
    if not creator:
        return jsonify({'error': '创建人不存在'}), 404
    
    priority = data.get('priority', 'medium')
    if priority not in ['high', 'medium', 'low']:
        return jsonify({'error': '优先级必须是 high、medium 或 low'}), 400
    
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': '截止日期格式无效'}), 400
    
    task = DispatchTask(
        title=data['title'],
        description=data.get('description'),
        assignee_id=data['assignee_id'],
        creator_id=data['creator_id'],
        status=data.get('status', 'pending'),
        priority=priority,
        due_date=due_date
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': '任务创建成功',
        'task': task.to_dict()
    }), 201


@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    per_page = min(per_page, 100)
    
    query = DispatchTask.query
    
    status = request.args.get('status')
    if status:
        if status not in ['pending', 'in_progress', 'completed']:
            return jsonify({'error': '状态必须是 pending、in_progress 或 completed'}), 400
        query = query.filter_by(status=status)
    
    priority = request.args.get('priority')
    if priority:
        if priority not in ['high', 'medium', 'low']:
            return jsonify({'error': '优先级必须是 high、medium 或 low'}), 400
        query = query.filter_by(priority=priority)
    
    assignee_id = request.args.get('assignee_id', type=int)
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    
    creator_id = request.args.get('creator_id', type=int)
    if creator_id:
        query = query.filter_by(creator_id=creator_id)
    
    query = query.order_by(DispatchTask.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'tasks': [task.to_dict() for task in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详情"""
    task = DispatchTask.query.get(task_id)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify({'task': task.to_dict()}), 200


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务信息"""
    task = DispatchTask.query.get(task_id)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400
    
    if data.get('title'):
        task.title = data['title']
    
    if 'description' in data:
        task.description = data['description']
    
    if data.get('priority'):
        if data['priority'] not in ['high', 'medium', 'low']:
            return jsonify({'error': '优先级必须是 high、medium 或 low'}), 400
        task.priority = data['priority']
    
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': '截止日期格式无效'}), 400
        else:
            task.due_date = None
    
    db.session.commit()
    
    return jsonify({
        'message': '任务更新成功',
        'task': task.to_dict()
    }), 200


@tasks_bp.route('/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """更新任务状态"""
    task = DispatchTask.query.get(task_id)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('status'):
        return jsonify({'error': '状态不能为空'}), 400
    
    new_status = data['status']
    if new_status not in ['pending', 'in_progress', 'completed']:
        return jsonify({'error': '状态必须是 pending、in_progress 或 completed'}), 400
    
    task.status = new_status
    
    if new_status == 'completed':
        task.completed_at = get_beijing_time()
    else:
        task.completed_at = None
    
    db.session.commit()
    
    return jsonify({
        'message': '任务状态更新成功',
        'task': task.to_dict()
    }), 200


@tasks_bp.route('/<int:task_id>/assign', methods=['PUT'])
def assign_task(task_id):
    """分配任务给指定用户"""
    task = DispatchTask.query.get(task_id)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('assignee_id'):
        return jsonify({'error': '执行人ID不能为空'}), 400
    
    assignee = User.query.get(data['assignee_id'])
    if not assignee:
        return jsonify({'error': '执行人不存在'}), 404
    
    task.assignee_id = data['assignee_id']
    
    db.session.commit()
    
    return jsonify({
        'message': '任务分配成功',
        'task': task.to_dict()
    }), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    task = DispatchTask.query.get(task_id)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': '任务删除成功'}), 200