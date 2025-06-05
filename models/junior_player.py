from app import db
from sqlalchemy import Enum

class JuniorPlayer(db.Model):
    __tablename__ = 'JuniorPlayers'  # Note the capitalization
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)  # Note the table name is capitalized
    squad_id = db.Column(db.Integer, db.ForeignKey('Squads.id'), nullable=True)  # Note the table name is capitalized and nullable=True
    
    # Guardian 1 Information
    guardian1_name = db.Column(db.String(100))  # Removed nullable=False constraint
    guardian1_relation = db.Column(db.Enum('Father', 'Mother', 'Grandparent', 'Guardian', 'Other'))  # Removed nullable=False constraint
    guardian1_tel = db.Column(db.String(20))  # Removed nullable=False constraint
    guardian1_address = db.Column(db.Text)  # Removed nullable=False constraint
    
    # Guardian 2 Information (Optional)
    guardian2_name = db.Column(db.String(100))
    guardian2_relation = db.Column(db.Enum('Father', 'Mother', 'Grandparent', 'Guardian', 'Other'))
    guardian2_tel = db.Column(db.String(20))
    guardian2_address = db.Column(db.Text)
    
    # Medical Information
    doctor_name = db.Column(db.String(100))  # Removed nullable=False constraint
    doctor_tel = db.Column(db.String(20))  # Removed nullable=False constraint
    doctor_address = db.Column(db.Text)  # Removed nullable=False constraint
    health_issues = db.Column(db.Text)
    
    # Rugby Information
    position = db.Column(Enum('Fullback', 'Wing', 'Centre', 'Fly Half', 'Scrum Half', 'Hooker', 'Prop', '2nd Row', 'Back Row', name='junior_player_positions_enum'), nullable=True)
    consent_signed = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)  # Age field, used to distinguish between adult and junior players
    
    user = db.relationship('User', backref=db.backref('junior_player', uselist=False))
    squad = db.relationship('Squad', backref=db.backref('junior_players', lazy=True))
    
    def __repr__(self):
        return f'<JuniorPlayer {self.id}>' 