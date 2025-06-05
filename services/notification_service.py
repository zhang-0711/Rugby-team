"""
Notification service for Simply Rugby.
This module provides functionality for sending and managing notifications to players and coaches.
"""
from app import db
from app.models.message import Message
from app.models.user import User
from app.models.member_assistant import MemberAssistant
from datetime import datetime


class NotificationService:
    """
    Service for managing and sending notifications to users.
    """
    
    @staticmethod
    def send_notification(sender_id, receiver_ids, content, message_type='announcement', title=None):
        """
        Send a notification to multiple receivers.
        
        Args:
            sender_id (int): ID of the sender (MemberAssistant)
            receiver_ids (list): List of receiver user IDs
            content (str): Message content
            message_type (str): Type of message (training, match, personal, announcement)
            title (str, optional): Message title
            
        Returns:
            bool: Success status
        """
        try:
            messages = []
            
            for receiver_id in receiver_ids:
                message = Message(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    title=title,
                    content=content,
                    message_type=message_type,
                    created_at=datetime.utcnow(),
                    is_read=False
                )
                messages.append(message)
            
            db.session.bulk_save_objects(messages)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error sending notifications: {str(e)}")
            return False
            
    @staticmethod
    def send_notification_to_squad(sender_id, squad_id, content, message_type='training', title=None):
        """
        Send a notification to all players in a specific squad.
        
        Args:
            sender_id (int): ID of the sender (MemberAssistant)
            squad_id (int): ID of the squad
            content (str): Message content
            message_type (str): Type of message
            title (str, optional): Message title
            
        Returns:
            bool: Success status
        """
        try:
            # Find all players in the squad
            # This query needs to be adjusted based on actual model relationships
            player_users = db.session.query(User.id).join(
                User.player).filter_by(squad_id=squad_id).all()
                
            junior_player_users = db.session.query(User.id).join(
                User.junior_player).filter_by(squad_id=squad_id).all()
            
            # Combine player IDs from both regular and junior players
            player_ids = [p[0] for p in player_users] + [p[0] for p in junior_player_users]
            
            if not player_ids:
                return False
                
            return NotificationService.send_notification(
                sender_id, player_ids, content, message_type, title)
        
        except Exception as e:
            print(f"Error sending notifications to squad: {str(e)}")
            return False
    
    @staticmethod
    def send_notification_to_coaches(sender_id, content, message_type='announcement', title=None):
        """
        Send a notification to all coaches.
        
        Args:
            sender_id (int): ID of the sender (MemberAssistant)
            content (str): Message content
            message_type (str): Type of message
            title (str, optional): Message title
            
        Returns:
            bool: Success status
        """
        try:
            # Find all coaches
            coach_users = db.session.query(User.id).join(
                User.coach).all()
            
            coach_ids = [c[0] for c in coach_users]
            
            if not coach_ids:
                return False
                
            return NotificationService.send_notification(
                sender_id, coach_ids, content, message_type, title)
        
        except Exception as e:
            print(f"Error sending notifications to coaches: {str(e)}")
            return False
    
    @staticmethod
    def mark_as_read(message_id, user_id):
        """
        Mark a specific message as read.
        
        Args:
            message_id (int): ID of the message
            user_id (int): ID of the user who is marking the message
            
        Returns:
            bool: Success status
        """
        try:
            message = Message.query.filter_by(
                id=message_id, 
                receiver_id=user_id
            ).first()
            
            if not message:
                return False
                
            message.is_read = True
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error marking message as read: {str(e)}")
            return False
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=50, offset=0):
        """
        Get notifications for a specific user.
        
        Args:
            user_id (int): User ID
            unread_only (bool): Whether to get only unread notifications
            limit (int): Maximum number of notifications to return
            offset (int): Offset for pagination
            
        Returns:
            list: List of notification objects
        """
        query = Message.query.filter_by(receiver_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
            
        notifications = query.order_by(
            Message.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return notifications
    
    @staticmethod
    def get_unread_count(user_id):
        """
        Get the count of unread notifications for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            int: Count of unread notifications
        """
        return Message.query.filter_by(
            receiver_id=user_id, 
            is_read=False
        ).count()
