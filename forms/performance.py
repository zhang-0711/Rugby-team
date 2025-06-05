from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, HiddenField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange

class PlayerPerformanceForm(FlaskForm):
    """球员比赛表现评估表单"""
    player_id = SelectField('选择球员', coerce=int, validators=[DataRequired()])
    match_id = SelectField('选择比赛', coerce=int, validators=[DataRequired()])
    
    # 比赛统计数据
    minutes_played = IntegerField('上场时间（分钟）', validators=[DataRequired(), NumberRange(min=0, max=80)])
    position_played = SelectField('场上位置', choices=[
        ('prop', '支柱'),
        ('hooker', '勾子'),
        ('lock', '锁定'),
        ('flanker', '侧锋'),
        ('number_8', '8号'),
        ('scrum_half', '半前锋'),
        ('fly_half', '半开'),
        ('center', '中锋'),
        ('wing', '边锋'),
        ('full_back', '后卫')
    ])
    
    # 技术表现评分
    passing_rating = SelectField('传球评分', coerce=int, choices=[(i, str(i)) for i in range(1, 6)])
    tackling_rating = SelectField('擒抱评分', coerce=int, choices=[(i, str(i)) for i in range(1, 6)])
    kicking_rating = SelectField('踢球评分', coerce=int, choices=[(i, str(i)) for i in range(1, 6)])
    
    # 比赛统计
    tries_scored = IntegerField('达阵数', default=0, validators=[NumberRange(min=0)])
    conversions = IntegerField('达阵转换次数', default=0, validators=[NumberRange(min=0)])
    penalties = IntegerField('罚球数', default=0, validators=[NumberRange(min=0)])
    line_outs_won = IntegerField('边线球赢取次数', default=0, validators=[NumberRange(min=0)])
    tackles_made = IntegerField('完成的擒抱数', default=0, validators=[NumberRange(min=0)])
    tackles_missed = IntegerField('未完成的擒抱数', default=0, validators=[NumberRange(min=0)])
    
    # 评价
    strengths = TextAreaField('优势', validators=[Optional()])
    weaknesses = TextAreaField('弱点', validators=[Optional()])
    improvement_areas = TextAreaField('需要改进的区域', validators=[Optional()])
    coach_comments = TextAreaField('教练评语', validators=[Optional()])
    
    # 其他
    yellow_cards = IntegerField('黄牌数', default=0, validators=[NumberRange(min=0)])
    red_cards = IntegerField('红牌数', default=0, validators=[NumberRange(min=0)])
    injury_details = TextAreaField('伤病情况', validators=[Optional()])
