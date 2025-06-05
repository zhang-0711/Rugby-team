from app import db
from datetime import datetime
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import relationship

class Message(db.Model):
    __tablename__ = 'Messages' # 假设数据库中的表名是 Messages

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, ForeignKey('MemberAssistants.id'), nullable=False) # Changed target table
    receiver_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False) # 参考 Users 表
    title = db.Column(db.String(255), nullable=True) # 新增标题字段，最大255字符，允许为空以兼容已有数据
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False) # 是否已读
    message_type = db.Column(Enum('training', 'match', 'personal', 'announcement', name='message_type_enum'), default='personal') # 消息类型

    # 关系 (可选，但有助于查询)
    sender = relationship('MemberAssistant', foreign_keys=[sender_id], backref='sent_messages') # Changed relationship target
    receiver = relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.receiver_id}>'
