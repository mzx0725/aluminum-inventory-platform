"""
统计分析路由蓝图
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_, or_
from app import db
from app.models import (
    User, AluminumPlate, Inventory, 
    InboundRecord, OutboundRecord, 
    DispatchTask, InventoryCheck
)
from app.utils.time_utils import get_beijing_time

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/overview', methods=['GET'])
def get_overview():
    """获取统计概览"""
    try:
        now = get_beijing_time()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_inventory = db.session.query(
            func.sum(Inventory.quantity)
        ).scalar() or 0
        
        today_inbound = db.session.query(
            func.sum(InboundRecord.quantity)
        ).filter(
            InboundRecord.inbound_time >= today_start
        ).scalar() or 0
        
        today_outbound = db.session.query(
            func.sum(OutboundRecord.quantity)
        ).filter(
            and_(
                OutboundRecord.outbound_time >= today_start,
                OutboundRecord.status == 'approved'
            )
        ).scalar() or 0
        
        pending_outbound = OutboundRecord.query.filter_by(
            status='pending'
        ).count()
        
        low_stock_warning = db.session.query(Inventory).filter(
            Inventory.quantity <= Inventory.warning_threshold
        ).count()
        
        pending_tasks = DispatchTask.query.filter(
            DispatchTask.status.in_(['pending', 'in_progress'])
        ).count()
        
        return jsonify({
            'total_inventory': total_inventory,
            'today_inbound': today_inbound,
            'today_outbound': today_outbound,
            'pending_outbound': pending_outbound,
            'low_stock_warning': low_stock_warning,
            'pending_tasks': pending_tasks
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计概览失败: {str(e)}'}), 500


@statistics_bp.route('/inventory', methods=['GET'])
def get_inventory_statistics():
    """获取库存统计"""
    try:
        by_model = db.session.query(
            AluminumPlate.model,
            AluminumPlate.specification,
            func.sum(Inventory.quantity).label('total_quantity'),
            func.count(Inventory.id).label('batch_count')
        ).join(
            Inventory, AluminumPlate.id == Inventory.plate_id
        ).group_by(
            AluminumPlate.id, AluminumPlate.model, AluminumPlate.specification
        ).all()
        
        model_stats = []
        for item in by_model:
            model_stats.append({
                'model': item.model,
                'specification': item.specification,
                'total_quantity': item.total_quantity or 0,
                'batch_count': item.batch_count
            })
        
        by_location = db.session.query(
            Inventory.location,
            func.sum(Inventory.quantity).label('total_quantity'),
            func.count(Inventory.id).label('batch_count')
        ).filter(
            Inventory.location.isnot(None)
        ).group_by(
            Inventory.location
        ).all()
        
        location_stats = []
        for item in by_location:
            location_stats.append({
                'location': item.location,
                'total_quantity': item.total_quantity or 0,
                'batch_count': item.batch_count
            })
        
        return jsonify({
            'by_model': model_stats,
            'by_location': location_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取库存统计失败: {str(e)}'}), 500


@statistics_bp.route('/trend', methods=['GET'])
def get_trend():
    """获取出入库趋势"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        group_by = request.args.get('group_by', 'day')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': '请提供开始日期和结束日期'}), 400
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            return jsonify({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}), 400
        
        if start_date > end_date:
            return jsonify({'error': '开始日期不能晚于结束日期'}), 400
        
        if group_by == 'day':
            date_format = func.strftime('%Y-%m-%d', InboundRecord.inbound_time)
            date_format_out = func.strftime('%Y-%m-%d', OutboundRecord.outbound_time)
        elif group_by == 'week':
            date_format = func.strftime('%Y-%W', InboundRecord.inbound_time)
            date_format_out = func.strftime('%Y-%W', OutboundRecord.outbound_time)
        elif group_by == 'month':
            date_format = func.strftime('%Y-%m', InboundRecord.inbound_time)
            date_format_out = func.strftime('%Y-%m', OutboundRecord.outbound_time)
        else:
            return jsonify({'error': 'group_by 参数必须是 day、week 或 month'}), 400
        
        inbound_trend = db.session.query(
            date_format.label('period'),
            func.sum(InboundRecord.quantity).label('inbound_quantity')
        ).filter(
            and_(
                InboundRecord.inbound_time >= start_date,
                InboundRecord.inbound_time <= end_date
            )
        ).group_by(
            'period'
        ).all()
        
        outbound_trend = db.session.query(
            date_format_out.label('period'),
            func.sum(OutboundRecord.quantity).label('outbound_quantity')
        ).filter(
            and_(
                OutboundRecord.outbound_time >= start_date,
                OutboundRecord.outbound_time <= end_date,
                OutboundRecord.status == 'approved'
            )
        ).group_by(
            'period'
        ).all()
        
        trend_dict = {}
        
        for item in inbound_trend:
            if item.period:
                trend_dict[item.period] = {
                    'period': item.period,
                    'inbound_quantity': item.inbound_quantity or 0,
                    'outbound_quantity': 0
                }
        
        for item in outbound_trend:
            if item.period:
                if item.period in trend_dict:
                    trend_dict[item.period]['outbound_quantity'] = item.outbound_quantity or 0
                else:
                    trend_dict[item.period] = {
                        'period': item.period,
                        'inbound_quantity': 0,
                        'outbound_quantity': item.outbound_quantity or 0
                    }
        
        trends = sorted(trend_dict.values(), key=lambda x: x['period'])
        
        return jsonify({
            'trends': trends,
            'group_by': group_by,
            'start_date': start_date_str,
            'end_date': end_date_str
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取趋势数据失败: {str(e)}'}), 500