from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms.auth import LoginForm, CoachForm, JuniorPlayerForm, PlayerForm, NonPlayerMemberForm, AdminResetPasswordForm
from app.forms import ResetPasswordForm
from app.models.user import User
from app.models.coach import Coach
from app.models.junior_player import JuniorPlayer
from app.models.player import Player
from app.models.non_player_member import NonPlayerMember
from app.models.squad import Squad
from app.utils.player_utils import ensure_player_records
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Check and fix missing player records before login
            if user.user_type in ['junior_player', 'player']:
                try:
                    ensure_player_records()
                except Exception as e:
                    print(f"Warning: Error in ensure_player_records: {str(e)}")
            
            login_user(user, remember=form.remember.data)
            
            # 按照建议，强制基于用户类型重定向，忽略 next_page 参数
            # 这样可以避免 session 刷新问题
            if user.user_type == 'player':
                return redirect(url_for('player.dashboard'))
            elif user.user_type == 'junior_player':
                print(f"DEBUG: 重定向到 junior_player.dashboard，用户类型为 {user.user_type}")
                return redirect(url_for('junior_player.dashboard'))
            elif user.user_type == 'coach':
                return redirect(url_for('coach.dashboard'))
            else:
                return redirect(url_for('main.index'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register/coach', methods=['GET', 'POST'])
def register_coach():
    form = CoachForm()
    
    # Directly load all teams (four fixed teams)
    squads = Squad.query.all()
    form.squad_id.choices = [(s.id, s.name) for s in squads]
    
    if form.validate_on_submit():
        try:
            # Get the selected team
            squad = Squad.query.get(form.squad_id.data)
            if not squad:
                flash('Selected team does not exist', 'danger')
                return render_template('auth/register_coach.html', title='Register as Coach', form=form)
            
            # Create user
            user = User(
                username=form.username.data,
                name=form.name.data,
                sru_number=form.sru_number.data,
                dob=datetime.strptime(form.dob.data, '%Y-%m-%d').date() if form.dob.data else None,
                address=form.address.data,
                tel_number=form.tel_number.data,
                mobile_number=form.mobile_number.data,
                email=form.email.data,
                postcode=form.postcode.data,
                user_type='coach'
            )
            user.set_password(form.password.data)
            
            # Add user to database
            db.session.add(user)
            db.session.flush()
            
            # Create coach record, specify team
            coach = Coach(user=user, squad_id=squad.id)
            
            db.session.add(coach)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('auth/register_coach.html', title='Register as Coach', form=form)
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_coach.html', title='Register as Coach', form=form)

@bp.route('/register/junior', methods=['GET', 'POST'])
def register_junior():
    form = JuniorPlayerForm()
    if request.method == 'POST':
        print(f"DEBUG: Form submitted with data: {request.form}")  # Print form data for debugging
        
        if form.validate_on_submit():
            try:
                # 创建用户
                user = User(
                    username=form.username.data,
                    name=form.name.data,
                    sru_number=form.sru_number.data,
                    dob=datetime.strptime(form.dob.data, '%Y-%m-%d').date() if form.dob.data else None,
                    address=form.address.data,
                    tel_number=form.tel_number.data,
                    mobile_number=form.mobile_number.data,
                    email=form.email.data,
                    postcode=form.postcode.data,
                    user_type='junior_player'  # Directly set user type as junior player
                )
                user.set_password(form.password.data)
                
                # Add user to database session and commit immediately to get user ID
                db.session.add(user)
                db.session.flush()  # 刷新会话以获取用户ID但不提交事务
                
                # Create junior player profile
                junior_player = JuniorPlayer(
                    user_id=user.id,  # 明确设置外键
                    guardian1_name=form.guardian1_name.data,
                    guardian1_relation=form.guardian1_relation.data,
                    guardian1_tel=form.guardian1_tel.data,
                    guardian1_address=form.guardian1_address.data,
                    guardian2_name=form.guardian2_name.data,
                    guardian2_relation=form.guardian2_relation.data if form.guardian2_name.data else None,
                    guardian2_tel=form.guardian2_tel.data if form.guardian2_name.data else None,
                    guardian2_address=form.guardian2_address.data if form.guardian2_name.data else None,
                    doctor_name=form.doctor_name.data,
                    doctor_tel=form.doctor_tel.data,
                    doctor_address=form.doctor_address.data,
                    health_issues=form.health_issues.data,
                    position=form.position.data,
                    consent_signed=form.consent_signed.data,
                    age=int(form.age.data) if form.age.data else None  # 添加年龄字段
                )
                
                # 添加青少年球员档案到数据库会话
                db.session.add(junior_player)
                
                # 提交整个事务
                db.session.commit()
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()  # 出错时回滚事务
                flash(f'Registration failed: {str(e)}', 'danger')
                print(f"ERROR: Registration failed with exception: {str(e)}")  # 打印错误信息进行调试
        else:
            # 显示表单验证错误
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                    print(f"VALIDATION ERROR: {field} - {error}")  # 打印验证错误进行调试
    
    return render_template('auth/register_junior.html', title='Register as Junior Player', form=form)

@bp.route('/register/player', methods=['GET', 'POST'])
def register_player():
    form = PlayerForm()
    if request.method == 'POST':
        print(f"DEBUG: Player form submitted with data: {request.form}")  # 打印表单数据进行调试
        
        if form.validate_on_submit():
            try:
                # 创建用户
                user = User(
                    username=form.username.data,
                    name=form.name.data,
                    sru_number=form.sru_number.data,
                    dob=datetime.strptime(form.dob.data, '%Y-%m-%d').date() if form.dob.data else None,
                    address=form.address.data,
                    tel_number=form.tel_number.data,
                    mobile_number=form.mobile_number.data,
                    email=form.email.data,
                    postcode=form.postcode.data,
                    user_type='player'  # 直接设置用户类型为成年球员
                )
                user.set_password(form.password.data)
                
                # 添加用户到数据库会话并刷新以获取ID
                db.session.add(user)
                db.session.flush()  # 刷新会话以获取用户ID但不提交事务
                
                # 创建成年球员档案
                player = Player(
                    user_id=user.id,  # 明确设置外键
                    next_of_kin=form.next_of_kin.data,
                    next_of_kin_relation=form.next_of_kin_relation.data,
                    next_of_kin_tel=form.next_of_kin_tel.data,
                    doctor_name=form.doctor_name.data,
                    doctor_tel=form.doctor_tel.data,
                    doctor_address=form.doctor_address.data,
                    health_issues=form.health_issues.data,
                    preferred_positions=form.preferred_positions.data,
                    age=int(form.age.data) if form.age.data else None  # 添加年龄字段
                )
                
                # 添加成年球员档案到数据库会话
                db.session.add(player)
                
                # 提交整个事务
                db.session.commit()
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()  # 出错时回滚事务
                flash(f'Registration failed: {str(e)}', 'danger')
                print(f"ERROR: Registration failed with exception: {str(e)}")  # 打印错误信息进行调试
        else:
            # 显示表单验证错误
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                    print(f"VALIDATION ERROR: {field} - {error}")  # 打印验证错误进行调试
    
    return render_template('auth/register_player.html', title='Register as Player', form=form)

@bp.route('/register/non-player', methods=['GET', 'POST'])
def register_non_player():
    form = NonPlayerMemberForm()
    if request.method == 'POST':
        print(f"DEBUG: Non-Player form submitted with data: {request.form}")  # 打印表单数据进行调试
        
        if form.validate_on_submit():
            try:
                # 创建用户
                user = User(
                    username=form.username.data,
                    name=form.name.data,
                    sru_number=form.sru_number.data,
                    dob=datetime.strptime(form.dob.data, '%Y-%m-%d').date() if form.dob.data else None,
                    address=form.address.data,
                    tel_number=form.tel_number.data,
                    mobile_number=form.mobile_number.data,
                    email=form.email.data,
                    postcode=form.postcode.data,
                    user_type='non_player_member'  # 直接设置用户类型为非球员会员
                )
                user.set_password(form.password.data)
                
                # 添加用户到数据库会话并刷新以获取ID
                db.session.add(user)
                db.session.flush()  # 刷新会话以获取用户ID但不提交事务
                
                # 创建非球员会员档案
                non_player = NonPlayerMember(
                    user_id=user.id,  # 明确设置外键
                    role_type=form.role_type.data
                )
                
                # 添加非球员会员档案到数据库会话
                db.session.add(non_player)
                
                # 提交整个事务
                db.session.commit()
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()  # 出错时回滚事务
                flash(f'Registration failed: {str(e)}', 'danger')
                print(f"ERROR: Registration failed with exception: {str(e)}")  # 打印错误信息进行调试
        else:
            # 显示表单验证错误
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                    print(f"VALIDATION ERROR: {field} - {error}")  # 打印验证错误进行调试
    
    return render_template('auth/register_non_player.html', title='Register as Non-Player Member', form=form) 

# Route for resetting password using old password
@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm() # Uses the import added earlier
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user:
            flash('Username not found.', 'danger')
            return render_template('auth/reset_password.html', title='Reset Password', form=form)
            
        try:
            # Attempt to check the old password
            # This is where the ValueError might occur for old 'scrypt' hashes
            if user.check_password(form.old_password.data):
                # Old password is correct, set the new one
                user.set_password(form.new_password.data) # Uses the updated method with pbkdf2:sha256
                db.session.commit()
                flash('Your password has been successfully reset. Please login with your new password.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid old password.', 'danger')
        except ValueError as e:
            # Catch the specific error related to unsupported hash types
            if 'unsupported hash type' in str(e):
                flash('Could not verify your old password due to a system compatibility issue. Please contact an administrator for help resetting your password.', 'danger')
                print(f"ERROR: Password check failed for user {user.username} due to unsupported hash: {e}")
            else:
                # Handle other potential ValueErrors during password check
                flash('An unexpected error occurred while verifying your password.', 'danger')
                print(f"ERROR: Unexpected ValueError during password check for user {user.username}: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'danger')
            print(f"ERROR: Unexpected exception during password reset for user {user.username}: {e}")

    return render_template('auth/reset_password.html', title='Reset Password', form=form)

# Admin route for resetting any user's password without old password verification
@bp.route('/admin/reset_password', methods=['GET', 'POST'])
def admin_reset_password():
    # Log user details for debugging
    print(f"Accessing reset password tool. User authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"User ID: {current_user.id}")
        print(f"User Role: {getattr(current_user, 'role', 'N/A')}")
        print(f"User Type: {getattr(current_user, 'user_type', 'N/A')}")

    # Check if the current user is either an admin or a member assistant
    if not current_user.is_authenticated or (current_user.role != 'admin' and current_user.user_type != 'member_assistant'):
        print(f"Permission denied for user {getattr(current_user, 'username', 'anonymous')}. Role: {getattr(current_user, 'role', 'N/A')}, Type: {getattr(current_user, 'user_type', 'N/A')}") # Add logging for denial
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))
        
    form = AdminResetPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user:
            flash(f'User {form.username.data} not found.', 'danger')
            return redirect(url_for('auth.admin_reset_password'))
        
        try:
            # Admin or Member Assistant can directly set the new password without verifying old password
            user.set_password(form.new_password.data) 
            db.session.commit()
            flash(f'Password for user {user.username} has been successfully reset.', 'success')
            return redirect(url_for('auth.admin_reset_password'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while resetting password: {str(e)}', 'danger')
            print(f"ERROR: Password reset failed for user {form.username.data}: {e}")
    
    # Updated title to reflect that both Admin and Member Assistant can use this tool
    return render_template('auth/admin_reset_password.html', title='Password Reset Tool', form=form)


@bp.route('/member_assistant/reset_password', methods=['GET', 'POST'])
def member_assistant_reset_password():
    # Log user details for debugging
    print(f"Accessing member assistant reset password tool. User authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"User ID: {current_user.id}")
        print(f"User Role: {getattr(current_user, 'role', 'N/A')}")
        print(f"User Type: {getattr(current_user, 'user_type', 'N/A')}")

    # Check if the current user is a member assistant
    if not current_user.is_authenticated or current_user.user_type != 'member_assistant':
        print(f"Permission denied for user {getattr(current_user, 'username', 'anonymous')}. Not a member assistant.")
        flash('只有会员助理可以访问此页面', 'danger')
        return redirect(url_for('main.index'))
        
    form = AdminResetPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user:
            flash(f'未找到用户 {form.username.data}', 'danger')
            return redirect(url_for('auth.member_assistant_reset_password'))
        
        try:
            # Member Assistant can directly set the new password without verifying old password
            user.set_password(form.new_password.data) 
            db.session.commit()
            flash(f'用户 {user.username} 的密码已成功重置', 'success')
            return redirect(url_for('auth.member_assistant_reset_password'))
        except Exception as e:
            db.session.rollback()
            flash(f'重置密码时发生错误: {str(e)}', 'danger')
            print(f"ERROR: Password reset failed for user {form.username.data}: {e}")
    
    # Chinese title for member assistant page
    return render_template('auth/member_assistant_reset_password.html', title='会员助理密码重置工具', form=form)
