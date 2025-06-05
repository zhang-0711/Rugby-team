from datetime import datetime
from app import db

class YouthPlayer(db.Model):
    __tablename__ = 'youth_players'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), unique=True, nullable=False)
    squad_id = db.Column(db.Integer, db.ForeignKey('Squads.id'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(50))
    height = db.Column(db.Float)  # 身高（厘米）
    weight = db.Column(db.Float)  # 体重（公斤）
    medical_conditions = db.Column(db.Text)  # 医疗状况
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    parent_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('youth_player', uselist=False))
    squad = db.relationship('Squad', backref=db.backref('youth_players', lazy='dynamic'))

    def __repr__(self):
        return f'<YouthPlayer {self.user.username}>'

class PlayerPerformance(db.Model):
    __tablename__ = 'player_performances'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('youth_players.id'), nullable=False)
    training_session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    attendance = db.Column(db.Boolean, default=True)  # 是否出席
    performance_rating = db.Column(db.Integer)  # 1-5的评分
    skills_notes = db.Column(db.Text)  # 技能表现记录
    attitude_notes = db.Column(db.Text)  # 态度表现记录
    coach_notes = db.Column(db.Text)  # 教练评语
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    player = db.relationship('YouthPlayer', backref=db.backref('performances', lazy='dynamic'))
    training_session = db.relationship('TrainingSession', back_populates='performances', lazy=True)

    def __repr__(self):
        return f'<PlayerPerformance {self.player.user.username} - {self.training_session.date}>'