"""
Routes for handling notifications in the Simply Rugby application.
"""
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService
from app.models.member_assistant import MemberAssistant
from app.models.squad import Squad
from app.models.user import User
from app.models.coach import Coach
from app.models.junior_player import JuniorPlayer
from app.models.player import Player
from app.models.notification import Notification
from app import db

# Create a Blueprint for the notification routes
notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications/management')
@login_required
def notification_management():
    """
    Render the notification management page.
    This page is accessible to both admin users and member assistants.
    """
    # Check if user is a member assistant or admin
    is_authorized = False
    
    if current_user.user_type == 'member_assistant':
        assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
        if assistant:
            is_authorized = True
    elif current_user.role == 'admin':
        is_authorized = True
        
    if not is_authorized:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))
        
    return render_template('notification/management.html')

@notification_bp.route('/api/users', methods=['GET'])
@login_required
def get_users():
    """
    Get all users in the system.
    
    Returns JSON with users array.
    This endpoint is used by the admin/member assistant dashboard.
    """
    # Check if user is authorized (admin or member assistant)
    is_authorized = False
    
    if current_user.user_type == 'member_assistant':
        assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
        if assistant:
            is_authorized = True
    elif current_user.role == 'admin':
        is_authorized = True
        
    if not is_authorized:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    # Get all users
    users = User.query.all()
    user_list = []
    
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'email': user.email if user.email else ''
        }
        user_list.append(user_data)
    
    return jsonify(user_list)

@notification_bp.route('/api/squads', methods=['GET'])
@login_required
def get_squads():
    """
    Get all squads in the system.
    
    Returns JSON with squads array.
    This endpoint is used by the admin/member assistant dashboard.
    """
    # Check if user is authorized (admin or member assistant)
    is_authorized = False
    
    if current_user.user_type == 'member_assistant':
        assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
        if assistant:
            is_authorized = True
    elif current_user.role == 'admin':
        is_authorized = True
        
    if not is_authorized:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    # Get all squads
    squads = Squad.query.all()
    squad_list = []
    
    for squad in squads:
        squad_data = {
            'id': squad.id,
            'name': squad.name,
            'team_type': squad.team_type
        }
        squad_list.append(squad_data)
    
    return jsonify(squad_list)

@notification_bp.route('/api/notifications/recent', methods=['GET'])
@login_required
def get_recent_notifications():
    """
    Get recent notifications sent by admins and member assistants.
    
    Returns JSON with notifications array.
    This endpoint is used by the admin/member assistant dashboard.
    """
    # Check if user is authorized (admin or member assistant)
    is_authorized = False
    
    if current_user.user_type == 'member_assistant':
        assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
        if assistant:
            is_authorized = True
    elif current_user.role == 'admin':
        is_authorized = True
        
    if not is_authorized:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    # Get recent notifications (limit to 50)
    # 使用简化的查询以避免复杂的join
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(50).all()
    
    notification_list = []
    for notification in notifications:
        # 查找发送者信息
        sender = User.query.get(notification.sender_id)
        sender_name = sender.username if sender else 'Unknown'
        
        # 确定接收者信息
        recipient_name = 'All Users'
        if notification.recipient_type == 'user' and notification.recipient_id:
            user = User.query.get(notification.recipient_id)
            recipient_name = user.username if user else 'Unknown User'
        elif notification.recipient_type == 'squad' and notification.squad_id:
            squad = Squad.query.get(notification.squad_id)
            recipient_name = squad.name if squad else 'Unknown Squad'
    
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'created_at': notification.created_at.isoformat() if hasattr(notification.created_at, 'isoformat') else str(notification.created_at),
            'sender_id': notification.sender_id,
            'sender_name': sender_name,
            'recipient_type': notification.recipient_type,
            'recipient_name': recipient_name
        }
        notification_list.append(notification_data)
    
    return jsonify(notification_list)

@notification_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """
    Get notifications for the current user.
    
    Query parameters:
    - unread_only: boolean (default: false)
    - limit: int (default: 20)
    - offset: int (default: 0)
    
    Returns JSON with notifications array.
    """
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    notifications = NotificationService.get_user_notifications(
        current_user.id, 
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    # Convert notifications to dictionary format for JSON response
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'content': notification.content,
            'sender_id': notification.sender_id,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read,
            'message_type': notification.message_type
        })
    
    return jsonify({
        'success': True,
        'notifications': notifications_data,
        'total_unread': NotificationService.get_unread_count(current_user.id)
    })

@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """
    Mark a notification as read.
    
    Parameters:
    - notification_id: ID of the notification to mark as read
    
    Returns JSON with success status.
    """
    success = NotificationService.mark_as_read(notification_id, current_user.id)
    
    return jsonify({
        'success': success,
        'total_unread': NotificationService.get_unread_count(current_user.id)
    })

@notification_bp.route('/api/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """
    Send a notification via JSON API.
    
    This endpoint requires a JSON payload with:
    - receiver_ids: Array of user IDs (optional if squad_id is provided)
    - squad_id: ID of the squad to send notification to (optional if receiver_ids is provided)
    - content: Notification content
    - message_type: Type of message (training, match, personal, announcement)
    
    Returns JSON with success status.
    """
    # Check if the user is a member assistant (not schedule assistant)
    assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
    if not assistant or current_user.user_type == 'schedule_assistant':
        return jsonify({
            'success': False,
            'message': 'Only member assistants can send notifications'
        }), 403
    
    data = request.json
    content = data.get('content')
    message_type = data.get('message_type', 'announcement')
    
    if not content:
        return jsonify({
            'success': False,
            'message': 'Content is required'
        }), 400
    
    # Send to specific receivers
    if 'receiver_ids' in data:
        receiver_ids = data['receiver_ids']
        success = NotificationService.send_notification(
            assistant.id, receiver_ids, content, message_type
        )
    # Send to a squad
    elif 'squad_id' in data:
        squad_id = data['squad_id']
        success = NotificationService.send_notification_to_squad(
            assistant.id, squad_id, content, message_type
        )
    # Send to all coaches
    elif data.get('send_to_coaches', False):
        success = NotificationService.send_notification_to_coaches(
            assistant.id, content, message_type
        )
    else:
        return jsonify({
            'success': False,
            'message': 'Either receiver_ids, squad_id, or send_to_coaches must be provided'
        }), 400
    
    return jsonify({
        'success': success,
        'message': 'Notification sent successfully' if success else 'Failed to send notification'
    })


@notification_bp.route('/api/form/notifications/send', methods=['POST'])
@login_required
def send_notification_form():
    """
    Send a notification via form submission.
    
    This endpoint handles form data with:
    - target_type: Type of receivers (all, coaches, etc.)
    - content: Notification content
    - message_type: Type of message
    - title: Notification title (optional)
    
    Redirects to the notification view with a flash message.
    """
    # 记录请求调试信息
    app.logger.debug(f"Form Data: {request.form}")
    app.logger.debug(f"Headers: {request.headers}")
    
    # 检查用户权限
    assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
    if not assistant or current_user.user_type == 'schedule_assistant':
        flash('只有会员助理可以发送通知', 'danger')
        return redirect(url_for('notification.send_notification_view', error='权限不足'))
    
    # 获取表单数据
    content = request.form.get('content')
    message_type = request.form.get('message_type', 'announcement')
    target_type = request.form.get('target_type')
    title = request.form.get('title')  # 新增: 获取通知标题
    
    # 验证必填字段
    if not content:
        flash('内容不能为空', 'danger')
        return redirect(url_for('notification.send_notification_view', error='内容不能为空'))
    
    success = False
    
    # 根据目标类型发送通知
    if target_type == 'all':
        # 发送给所有用户的逻辑
        # 这里简化为只发送给所有教练
        success = NotificationService.send_notification_to_coaches(
            assistant.id, content, message_type, title
        )
    elif target_type == 'coaches':
        # 发送给所有教练
        success = NotificationService.send_notification_to_coaches(
            assistant.id, content, message_type, title
        )
    elif target_type == 'squad':
        # 发送给特定球队
        squad_id = request.form.get('squad_id')
        if squad_id:
            success = NotificationService.send_notification_to_squad(
                assistant.id, int(squad_id), content, message_type, title
            )
        else:
            flash('请选择要发送的球队', 'danger')
            return redirect(url_for('notification.send_notification_view', error='未选择球队'))
    else:
        flash('请选择有效的接收者类型', 'danger')
        return redirect(url_for('notification.send_notification_view', error='无效的接收者类型'))
    
    if success:
        flash('通知发送成功!', 'success')
    else:
        flash('通知发送失败，请稍后再试', 'danger')
    
    return redirect(url_for('notification.notifications_view'))

# Web views for notifications

@notification_bp.route('/notifications', methods=['GET'])
@login_required
def notifications_view():
    """
    Render the notifications page.
    """
    notifications = NotificationService.get_user_notifications(
        current_user.id, 
        limit=50
    )
    
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    return render_template(
        'notifications/index.html',
        notifications=notifications,
        unread_count=unread_count
    )

@notification_bp.route('/notifications/send', methods=['GET', 'POST'])
@login_required
def send_notification_view():
    """
    View for sending notifications.
    
    Renders the send notification template.
    """
    # Only member assistants can view this page
    assistant = MemberAssistant.query.filter_by(user_id=current_user.id).first()
    if not assistant or current_user.user_type == 'schedule_assistant':
        flash('只有会员助理可以发送通知', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取URL参数
    error = request.args.get('error')
    debug_info = None
    
    # 开发模式下显示调试信息
    if app.debug:
        debug_info = {
            'request_method': request.method,
            'form_data': dict(request.form) if request.method == 'POST' else None,
            'headers': dict(request.headers),
            'url': request.url,
        }
        debug_info = str(debug_info)
    
    squads = Squad.query.all()
    return render_template('notifications/send.html', 
                          squads=squads, 
                          error=error,
                          debug_info=debug_info)
