from app import db
from sqlalchemy import Enum

class Game(db.Model):
    __tablename__ = 'Games' # Match DB table name

    # Define at least a primary key
    id = db.Column(db.Integer, primary_key=True)

    # Add squad_id for relation with squads
    squad_id = db.Column(db.Integer, db.ForeignKey('Squads.id'), nullable=True)  # 允许为空以便兼容既有数据
    
    # Other columns
    season_id = db.Column(db.Integer, db.ForeignKey('Seasons.id'), nullable=False)
    opponent = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.Date, nullable=False)
    kickoff_time = db.Column(db.Time, nullable=True)
    location = db.Column(Enum('home', 'away', name='game_location_enum'), nullable=False)
    score_for = db.Column(db.Integer, nullable=True)
    score_against = db.Column(db.Integer, nullable=True)
    result = db.Column(Enum('won', 'lost', 'drew', name='game_result_enum'), nullable=True)
    comments_half1 = db.Column(db.Text, nullable=True)
    comments_half2 = db.Column(db.Text, nullable=True)

    # Relationships
    season = db.relationship('Season')
    squad = db.relationship('Squad', backref=db.backref('games', lazy='dynamic'))
    # Add relationship for Evaluations if needed

    def __repr__(self):
        return f'<Game {self.id} vs {self.opponent} on {self.match_date}>'
