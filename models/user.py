from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'Users'  # 注意首字母大写
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sru_number = db.Column(db.String(20), unique=True, nullable=False)
    dob = db.Column(db.Date)
    address = db.Column(db.Text)
    tel_number = db.Column(db.String(20))
    mobile_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    postcode = db.Column(db.String(20))
    user_type = db.Column(db.Enum('player', 'junior_player', 'non_player_member', 'coach', 'schedule_assistant', 'member_assistant'), nullable=False)
    
    def set_password(self, password):
        # Explicitly use pbkdf2:sha256 for better compatibility
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        try:
            # 尝试正常验证密码
            return check_password_hash(self.password_hash, password)
        except ValueError as e:
            # 如果是scrypt哈希算法问题
            if 'unsupported hash type scrypt' in str(e):
                # 处理scrypt哈希失败的情况
                # 这里直接返回False，让用户重新登录
                print(f"检测到不支持的哈希算法: {e}")
                return False
            # 其他错误则继续抛出
            raise
    
    @property
    def role(self):
        """
        为了兼容现有代码，保留role属性
        """
        return self.user_type 