from app import db
from datetime import datetime

class MedicalRecord(db.Model):
    __tablename__ = 'MedicalRecords'
    
    id = db.Column(db.Integer, primary_key=True)
    junior_player_id = db.Column(db.Integer, db.ForeignKey('JuniorPlayers.id'), nullable=False)
    doctor_name = db.Column(db.String(100))
    doctor_phone = db.Column(db.String(20))
    doctor_email = db.Column(db.String(100))
    medical_conditions = db.Column(db.Text)
    allergies = db.Column(db.Text)
    medications = db.Column(db.Text)
    last_checkup_date = db.Column(db.Date)
    next_checkup_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    junior_player = db.relationship('JuniorPlayer', backref=db.backref('medical_records', lazy='dynamic'))
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} for JuniorPlayer {self.junior_player_id}>'
