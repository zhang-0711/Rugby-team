from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, TextAreaField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class PlayerForm(FlaskForm):
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    position = SelectField('Position', choices=[
        ('prop', 'Prop'),
        ('hooker', 'Hooker'),
        ('lock', 'Lock'),
        ('flanker', 'Flanker'),
        ('number8', 'Number 8'),
        ('scrumhalf', 'Scrum Half'),
        ('flyhalf', 'Fly Half'),
        ('centre', 'Centre'),
        ('wing', 'Wing'),
        ('fullback', 'Fullback')
    ], validators=[DataRequired()])
    jersey_number = IntegerField('Jersey Number', validators=[Optional(), NumberRange(min=1, max=99)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=100, max=250)])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=20, max=150)])
    preferred_foot = SelectField('Preferred Foot', choices=[
        ('left', 'Left'),
        ('right', 'Right'),
        ('both', 'Both')
    ], validators=[DataRequired()])
    medical_conditions = TextAreaField('Medical Conditions', validators=[Optional(), Length(max=500)])
    emergency_contact = StringField('Emergency Contact', validators=[DataRequired(), Length(max=100)])
    emergency_phone = StringField('Emergency Phone', validators=[DataRequired(), Length(max=20)])

class PlayerStatsForm(FlaskForm):
    attendance = BooleanField('Attendance', default=True)
    performance_rating = IntegerField('Performance Rating', validators=[Optional(), NumberRange(min=1, max=5)])
    distance_covered = FloatField('Distance Covered (m)', validators=[Optional(), NumberRange(min=0)])
    max_speed = FloatField('Max Speed (km/h)', validators=[Optional(), NumberRange(min=0)])
    avg_speed = FloatField('Average Speed (km/h)', validators=[Optional(), NumberRange(min=0)])
    sprints = IntegerField('Number of Sprints', validators=[Optional(), NumberRange(min=0)])
    tackles = IntegerField('Number of Tackles', validators=[Optional(), NumberRange(min=0)])
    passes = IntegerField('Number of Passes', validators=[Optional(), NumberRange(min=0)])
    pass_accuracy = FloatField('Pass Accuracy (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    coach_notes = TextAreaField('Coach Notes', validators=[Optional(), Length(max=500)]) 