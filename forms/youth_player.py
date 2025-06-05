from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, TextAreaField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange

class YouthPlayerForm(FlaskForm):
    date_of_birth = DateField('出生日期', validators=[DataRequired()])
    position = SelectField('位置', choices=[
        ('prop', '支柱'),
        ('hooker', '钩球手'),
        ('lock', '锁球手'),
        ('flanker', '侧翼前锋'),
        ('number8', '8号球员'),
        ('scrumhalf', '传锋'),
        ('flyhalf', '接锋'),
        ('centre', '中锋'),
        ('wing', '边锋'),
        ('fullback', '后卫')
    ], validators=[DataRequired()])
    height = FloatField('身高(cm)', validators=[Optional(), NumberRange(min=100, max=250)])
    weight = FloatField('体重(kg)', validators=[Optional(), NumberRange(min=20, max=150)])
    medical_conditions = TextAreaField('医疗状况', validators=[Optional(), Length(max=500)])
    emergency_contact = StringField('紧急联系人', validators=[DataRequired(), Length(max=100)])
    emergency_phone = StringField('紧急联系电话', validators=[DataRequired(), Length(max=20)])
    parent_name = StringField('家长姓名', validators=[DataRequired(), Length(max=100)])
    parent_phone = StringField('家长电话', validators=[DataRequired(), Length(max=20)])
    parent_email = StringField('家长邮箱', validators=[Optional(), Email(), Length(max=120)])

class PlayerPerformanceForm(FlaskForm):
    attendance = BooleanField('出席', default=True)
    performance_rating = IntegerField('表现评分', validators=[Optional(), NumberRange(min=1, max=5)])
    skills_notes = TextAreaField('技能表现', validators=[Optional(), Length(max=500)])
    attitude_notes = TextAreaField('态度表现', validators=[Optional(), Length(max=500)])
    coach_notes = TextAreaField('教练评语', validators=[Optional(), Length(max=500)]) 