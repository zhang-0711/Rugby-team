from app import db
from sqlalchemy import ForeignKey

class TrainingRecord(db.Model):
    __tablename__ = 'TrainingRecords'
    
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, ForeignKey('Coaches.id'), nullable=False)
    player_id = db.Column(db.Integer, ForeignKey('Players.id'), nullable=False)
    time = db.Column(db.Time, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    activities = db.Column(db.Text, nullable=True)
    injury_note = db.Column(db.Text, nullable=True)
    
    # 关联关系
    coach = db.relationship('Coach')
    player = db.relationship('Player')
    
    def __repr__(self):
        return f'<TrainingRecord {self.id} for Player {self.player_id} at {self.time}>'