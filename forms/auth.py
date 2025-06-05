from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, SelectField, BooleanField, SubmitField, HiddenField
from wtforms.widgets import DateInput
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class BaseUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Full Name', validators=[DataRequired()])
    sru_number = StringField('SRU Number', validators=[DataRequired()])
    dob = StringField('Date of Birth (YYYY-MM-DD)', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    tel_number = StringField('Telephone Number')
    mobile_number = StringField('Mobile Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[
        ('coach', 'Coach'),
        ('junior_player', 'Junior Player'),
        ('non_player_member', 'Non-Player Member')
    ], validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_sru_number(self, sru_number):
        user = User.query.filter_by(sru_number=sru_number.data).first()
        if user:
            raise ValidationError('SRU number already exists.')

class CoachForm(BaseUserForm):
    # 覆盖继承的user_type字段，设置默认值为coach
    user_type = HiddenField('User Type', default='coach')
    
    # 选择团队，直接显示四个球队
    squad_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Register as Coach')

class PlayerForm(BaseUserForm):
    # 覆盖继承的user_type字段，设置默认值为player，并使用HiddenField
    user_type = HiddenField('User Type', default='player')
    # 成年球员特有字段
    next_of_kin = StringField('Next of Kin Name', validators=[DataRequired()])
    next_of_kin_relation = SelectField('Next of kin type', choices=[
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Cousin', 'Cousin'),
        ('Friend', 'Friend'),
        ('Partner', 'Partner'),
        ('Spouse', 'Spouse'),
        ('Colleague', 'Colleague'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    next_of_kin_tel = StringField('Next of Kin Telephone', validators=[DataRequired()])
    doctor_name = StringField('Doctor Name', validators=[DataRequired()])
    doctor_tel = StringField('Doctor Telephone', validators=[DataRequired()])
    doctor_address = TextAreaField('Doctor Address', validators=[DataRequired()])
    health_issues = TextAreaField('Health Issues')
    preferred_positions = SelectField('Preferred Position', choices=[
        ('Fullback', 'Fullback'),
        ('Wing', 'Wing'),
        ('Centre', 'Centre'),
        ('Fly Half', 'Fly Half'),
        ('Scrum Half', 'Scrum Half'),
        ('Hooker', 'Hooker'),
        ('Prop', 'Prop'),
        ('2nd Row', '2nd Row'),
        ('Back Row', 'Back Row')
    ], validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    submit = SubmitField('Register as Player')

class JuniorPlayerForm(BaseUserForm):
    # 覆盖继承的user_type字段，设置默认值为junior_player，并使用HiddenField
    user_type = HiddenField('User Type', default='junior_player')
    guardian1_name = StringField('Guardian 1 Name', validators=[DataRequired()])
    guardian1_relation = SelectField('Guardian 1 Relation', choices=[
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Grandparent', 'Grandparent'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    guardian1_tel = StringField('Guardian 1 Telephone', validators=[DataRequired()])
    guardian1_address = TextAreaField('Guardian 1 Address', validators=[DataRequired()])
    guardian2_name = StringField('Guardian 2 Name')
    guardian2_relation = SelectField('Guardian 2 Relation', choices=[
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Grandparent', 'Grandparent'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other')
    ])
    guardian2_tel = StringField('Guardian 2 Telephone')
    guardian2_address = TextAreaField('Guardian 2 Address')
    doctor_name = StringField('Doctor Name', validators=[DataRequired()])
    doctor_tel = StringField('Doctor Telephone', validators=[DataRequired()])
    doctor_address = TextAreaField('Doctor Address', validators=[DataRequired()])
    health_issues = TextAreaField('Health Issues')
    position = SelectField('Preferred Position', choices=[
        ('Fullback', 'Fullback'),
        ('Wing', 'Wing'),
        ('Centre', 'Centre'),
        ('Fly Half', 'Fly Half'),
        ('Scrum Half', 'Scrum Half'),
        ('Hooker', 'Hooker'),
        ('Prop', 'Prop'),
        ('2nd Row', '2nd Row'),
        ('Back Row', 'Back Row')
    ], validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    consent_signed = BooleanField('I consent to my child participating in rugby activities')
    submit = SubmitField('Register as Junior Player')

class NonPlayerMemberForm(BaseUserForm):
    # 覆盖继承的user_type字段，设置默认值为non_player_member
    user_type = HiddenField('User Type', default='non_player_member')
    role_type = SelectField('Role Type', choices=[
        ('guardian', 'Guardian'),
        ('doctor', 'Doctor')
    ], validators=[DataRequired()])
    submit = SubmitField('Register as Non-Player Member')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    
class AdminResetPasswordForm(FlaskForm):
    """Form for administrators to reset any user's password without old password verification."""
    username = StringField('Username', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset User Password')
    
    def validate_username(self, username):
        # 确保用户存在
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('No user found with that username.')