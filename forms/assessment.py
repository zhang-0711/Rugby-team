from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class SkillAssessmentForm(FlaskForm):
    assessment_date = DateField('Assessment Date', validators=[DataRequired()])
    skill_type = SelectField('Skill Type', choices=[
        ('passing', 'Passing'),
        ('tackling', 'Tackling'),
        ('kicking', 'Kicking'),
        ('scrummaging', 'Scrummaging'),
        ('lineout', 'Lineout'),
        ('rucking', 'Rucking'),
        ('mauling', 'Mauling'),
        ('defense', 'Defense'),
        ('attack', 'Attack'),
        ('fitness', 'Fitness')
    ], validators=[DataRequired()])
    skill_level = IntegerField('Skill Level', validators=[
        DataRequired(),
        NumberRange(min=1, max=5)
    ])
    coach_notes = TextAreaField('Coach Notes', validators=[Optional(), Length(max=1000)])

class MatchRecordForm(FlaskForm):
    match_date = DateField('Match Date', validators=[DataRequired()])
    squad_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    opponent = StringField('Opponent', validators=[DataRequired(), Length(max=100)])
    season = StringField('Season', validators=[DataRequired(), Length(max=50)])
    result = SelectField('Result', choices=[
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('draw', 'Draw')
    ], validators=[DataRequired()])
    score = StringField('Score', validators=[Optional(), Length(max=20)])
    half_time_score = StringField('Half Time Score', validators=[Optional(), Length(max=20)])
    half_time_evaluation = TextAreaField('Half Time Evaluation', validators=[Optional(), Length(max=1000)])
    coach_id = SelectField('Coach', coerce=int, validators=[DataRequired()]) 