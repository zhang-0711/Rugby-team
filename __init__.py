from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os
import pymysql

# 使用 PyMySQL 替代 MySQLdb
pymysql.install_as_MySQLdb()

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)
    
    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['TESTING'] = False
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # --- Add User Loader --- 
    from .models import User # Import User model here
    @login_manager.user_loader
    def load_user(user_id):
        # Since the user_id is just the primary key of our user table,
        # use it in the query for the user
        return User.query.get(int(user_id))
    # --- End Add User Loader ---

    # 注册蓝图 - 延迟导入避免循环引用
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.coach import bp as coach_bp
    from .routes.player import bp as player_bp
    from .routes.junior_player import bp as junior_player_bp
    from .routes.admin import bp as admin_bp
    from .routes.training import bp as training_bp
    from .routes.skill_chart_api import skill_chart_api
    from .routes.test_routes import bp as test_bp
    from .routes.player_fix import bp as player_fix_bp
    from .routes.notification import notification_bp
    from .routes.member_assistant import assistant_bp
    from .routes.match_performance import match_performance_bp
    from .routes.schedule_assistant import bp as schedule_assistant_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp)
    app.register_blueprint(coach_bp, url_prefix='/coach')
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(junior_player_bp, url_prefix='/junior_player')
    app.register_blueprint(training_bp)
    app.register_blueprint(skill_chart_api)  # Register skill chart API blueprint
    app.register_blueprint(test_bp)  # Register test routes blueprint
    app.register_blueprint(player_fix_bp)  # Register player fix blueprint
    app.register_blueprint(notification_bp)  # Register notification routes blueprint
    app.register_blueprint(assistant_bp, url_prefix='/assistant')  # Register member assistant routes blueprint
    app.register_blueprint(match_performance_bp)  # Register match performance routes blueprint
    app.register_blueprint(schedule_assistant_bp)  # Register schedule assistant routes blueprint
    
    # 初始化数据库表
    # with app.app_context():
    #     db.create_all()
    
    return app 