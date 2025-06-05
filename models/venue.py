from app import db

class Venue(db.Model):
    __tablename__ = 'Venues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    facilities = db.Column(db.Text, nullable=True)  # 描述可用设施，如更衣室、停车场等
    is_home = db.Column(db.Boolean, default=False)  # 是否为主场
    contact_info = db.Column(db.String(255), nullable=True)  # 场地联系信息
    notes = db.Column(db.Text, nullable=True)  # 其他备注
    
    # 场地可用性信息可以通过单独的表来管理
    
    def __repr__(self):
        return f'<Venue {self.id}: {self.name}>'
