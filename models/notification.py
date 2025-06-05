from app import db
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50), default='general') # e.g., 'general', 'training', 'match', 'urgent'

    # Relationships (optional but helpful)
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_notifications')
    recipient = relationship('User', foreign_keys=[recipient_id], backref='received_notifications')

    def __repr__(self):
        return f'<Notification {self.id} from {self.sender_id} to {self.recipient_id}>'

    def mark_as_read(self):
        self.is_read = True
        db.session.add(self)
        db.session.commit()
