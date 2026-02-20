"""
数据库模型定义
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.utils.time_utils import get_beijing_time


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='warehouse')  # admin/warehouse/dispatcher
    status = db.Column(db.String(20), nullable=False, default='active')  # active/inactive
    created_at = db.Column(db.DateTime, nullable=False, default=get_beijing_time)
    
    # 关系
    inbound_records = db.relationship('InboundRecord', backref='operator', lazy='dynamic')
    outbound_applications = db.relationship('OutboundRecord', 
                                           foreign_keys='OutboundRecord.applicant_id',
                                           backref='applicant', lazy='dynamic')
    outbound_approvals = db.relationship('OutboundRecord', 
                                        foreign_keys='OutboundRecord.approver_id',
                                        backref='approver', lazy='dynamic')
    assigned_tasks = db.relationship('DispatchTask', 
                                    foreign_keys='DispatchTask.assignee_id',
                                    backref='assignee', lazy='dynamic')
    created_tasks = db.relationship('DispatchTask', 
                                   foreign_keys='DispatchTask.creator_id',
                                   backref='creator', lazy='dynamic')
    inventory_checks = db.relationship('InventoryCheck', backref='checker', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class AluminumPlate(db.Model):
    """铝板信息表"""
    __tablename__ = 'aluminum_plates'
    
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False, index=True)  # 型号
    specification = db.Column(db.String(200), nullable=False)  # 规格
    unit = db.Column(db.String(20), nullable=False, default='张')  # 单位
    supplier = db.Column(db.String(200))  # 供应商
    remark = db.Column(db.Text)  # 备注
    
    # 关系
    inventories = db.relationship('Inventory', backref='plate', lazy='dynamic')
    inbound_records = db.relationship('InboundRecord', backref='plate', lazy='dynamic')
    outbound_records = db.relationship('OutboundRecord', backref='plate', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model': self.model,
            'specification': self.specification,
            'unit': self.unit,
            'supplier': self.supplier,
            'remark': self.remark
        }
    
    def __repr__(self):
        return f'<AluminumPlate {self.model} - {self.specification}>'


class Inventory(db.Model):
    """库存表"""
    __tablename__ = 'inventories'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_id = db.Column(db.Integer, db.ForeignKey('aluminum_plates.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    location = db.Column(db.String(200))  # 存放位置
    batch_number = db.Column(db.String(100), index=True)  # 批次号
    warning_threshold = db.Column(db.Integer, default=10)  # 预警阈值
    last_updated = db.Column(db.DateTime, nullable=False, default=get_beijing_time, onupdate=get_beijing_time)
    
    # 关系
    inventory_checks = db.relationship('InventoryCheck', backref='inventory', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        plate_info = self.plate.to_dict() if self.plate else {}
        return {
            'id': self.id,
            'plate_id': self.plate_id,
            'plateCode': plate_info.get('model', ''),
            'specification': plate_info.get('specification', ''),
            'unit': plate_info.get('unit', '张'),
            'supplier': plate_info.get('supplier', ''),
            'totalQuantity': self.quantity,
            'availableQuantity': self.quantity,
            'reservedQuantity': 0,
            'defectiveQuantity': 0,
            'location': self.location,
            'batchNumber': self.batch_number,
            'warningThreshold': self.warning_threshold,
            'updatedAt': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def is_low_stock(self):
        """判断是否库存不足"""
        return self.quantity <= self.warning_threshold
    
    def __repr__(self):
        return f'<Inventory {self.plate_id} - {self.quantity}>'


class InboundRecord(db.Model):
    """入库记录表"""
    __tablename__ = 'inbound_records'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_id = db.Column(db.Integer, db.ForeignKey('aluminum_plates.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    batch_number = db.Column(db.String(100), index=True)
    supplier = db.Column(db.String(200))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    inbound_time = db.Column(db.DateTime, nullable=False, default=get_beijing_time, index=True)
    remark = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plate_id': self.plate_id,
            'plate': self.plate.to_dict() if self.plate else None,
            'quantity': self.quantity,
            'batch_number': self.batch_number,
            'supplier': self.supplier,
            'operator_id': self.operator_id,
            'operator': self.operator.real_name if self.operator else None,
            'inbound_time': self.inbound_time.isoformat() if self.inbound_time else None,
            'remark': self.remark
        }
    
    def __repr__(self):
        return f'<InboundRecord {self.id} - {self.plate_id}>'


class OutboundRecord(db.Model):
    """出库记录表"""
    __tablename__ = 'outbound_records'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_id = db.Column(db.Integer, db.ForeignKey('aluminum_plates.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)  # pending/approved/rejected
    outbound_time = db.Column(db.DateTime, index=True)
    remark = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plate_id': self.plate_id,
            'plate': self.plate.to_dict() if self.plate else None,
            'quantity': self.quantity,
            'applicant_id': self.applicant_id,
            'applicant': self.applicant.real_name if self.applicant else None,
            'approver_id': self.approver_id,
            'approver': self.approver.real_name if self.approver else None,
            'status': self.status,
            'outbound_time': self.outbound_time.isoformat() if self.outbound_time else None,
            'remark': self.remark
        }
    
    def __repr__(self):
        return f'<OutboundRecord {self.id} - {self.status}>'


class DispatchTask(db.Model):
    """调度任务表"""
    __tablename__ = 'dispatch_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)  # pending/in_progress/completed
    priority = db.Column(db.String(20), nullable=False, default='medium')  # high/medium/low
    due_date = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_beijing_time)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assignee_id': self.assignee_id,
            'assignee': self.assignee.real_name if self.assignee else None,
            'creator_id': self.creator_id,
            'creator': self.creator.real_name if self.creator else None,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<DispatchTask {self.id} - {self.title}>'


class InventoryCheck(db.Model):
    """盘点记录表"""
    __tablename__ = 'inventory_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'), nullable=False, index=True)
    expected_quantity = db.Column(db.Integer, nullable=False)  # 预期数量
    actual_quantity = db.Column(db.Integer, nullable=False)  # 实际数量
    difference = db.Column(db.Integer, nullable=False)  # 差异
    checker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    check_time = db.Column(db.DateTime, nullable=False, default=get_beijing_time, index=True)
    remark = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'inventory': self.inventory.to_dict() if self.inventory else None,
            'expected_quantity': self.expected_quantity,
            'actual_quantity': self.actual_quantity,
            'difference': self.difference,
            'checker_id': self.checker_id,
            'checker': self.checker.real_name if self.checker else None,
            'check_time': self.check_time.isoformat() if self.check_time else None,
            'remark': self.remark
        }
    
    def __repr__(self):
        return f'<InventoryCheck {self.id} - Diff: {self.difference}>'