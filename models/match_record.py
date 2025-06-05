from app import db
from datetime import datetime

class MatchRecord(db.Model):
    __tablename__ = 'match_records'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Players.id'))
    junior_player_id = db.Column(db.Integer, db.ForeignKey('JuniorPlayers.id'))
    squad_id = db.Column(db.Integer, db.ForeignKey('Squads.id'), nullable=False)
    match_date = db.Column(db.Date, nullable=False)
    opponent = db.Column(db.String(100), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(10), nullable=False)  # 'win', 'loss', 'draw'
    score = db.Column(db.String(20))  # e.g., '24-17'
    half_time_score = db.Column(db.String(20))
    half_time_evaluation = db.Column(db.Text)
    coach_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    player = db.relationship('Player', backref='match_records')
    junior_player = db.relationship('JuniorPlayer', backref='match_records')
    squad = db.relationship('Squad', backref='match_records')
    coach = db.relationship('User', backref='match_records')

    def __repr__(self):
        return f'<MatchRecord {self.match_date} vs {self.opponent}>' 