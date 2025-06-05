from app import db

class Coach(db.Model):
    __tablename__ = 'Coaches'  # 注意首字母大写
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)  # 注意表名大写
    squad_id = db.Column(db.Integer, db.ForeignKey('Squads.id'), nullable=True)  # 注意表名大写和nullable=True
    
    user = db.relationship('User', backref=db.backref('coach', uselist=False))
    squad = db.relationship('Squad', backref=db.backref('coaches', lazy=True))
    
    def __repr__(self):
        return f'<Coach {self.id}>' 