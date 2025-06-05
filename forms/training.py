from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime
from app.models.squad import Squad

class TrainingRecordForm(FlaskForm):
    date = DateField('Training Date', validators=[DataRequired()], default=datetime.today)
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    location = StringField('Location', validators=[DataRequired()])
    focus_area = StringField('Focus Area')
    attendance_count = IntegerField('Attendance Count', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes')
    squad_id = SelectField('Squad', coerce=int, validators=[DataRequired()])

class TrainingSearchForm(FlaskForm):
    query = StringField('Search Keyword', validators=[Optional()])
    squad_id = SelectField('Squad', coerce=int, validators=[Optional()])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(TrainingSearchForm, self).__init__(*args, **kwargs)
        self.squad_id.choices = [(0, 'All Squads')] + [(s.id, s.name) for s in Squad.query.order_by(Squad.name).all()] 