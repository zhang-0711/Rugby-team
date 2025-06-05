from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from datetime import datetime

class CoachProfileForm(FlaskForm):
    specialization = StringField('Specialization', validators=[Optional(), Length(max=100)])
    years_of_experience = IntegerField('Years of Experience', validators=[Optional(), NumberRange(min=0)])
    qualifications = TextAreaField('Qualifications')
    bio = TextAreaField('Bio')
    contact_number = StringField('Contact Number', validators=[Optional(), Length(max=20)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save Profile')

class TrainingPlanForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()], default=datetime.today)
    end_date = DateField('End Date', validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly')
    ], validators=[DataRequired()])
    squad_id = SelectField('Squad', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Plan')

class TrainingSessionForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], default=datetime.today)
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    focus_area = StringField('Focus Area', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Session') 