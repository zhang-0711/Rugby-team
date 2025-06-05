from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, FloatField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Email

class JuniorPlayerForm(FlaskForm):
    sru_number = StringField('SRU Number', validators=[DataRequired(), Length(max=20)])
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
    guardian_consent_signed = BooleanField('Guardian Consent Signed')
    guardian_consent_date = DateField('Guardian Consent Date', validators=[Optional()])

class GuardianForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    relationship = StringField('Relationship', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    is_primary = BooleanField('Primary Guardian')

class MedicalRecordForm(FlaskForm):
    doctor_name = StringField('Doctor Name', validators=[DataRequired(), Length(max=100)])
    doctor_phone = StringField('Doctor Phone', validators=[Optional(), Length(max=20)])
    doctor_email = StringField('Doctor Email', validators=[Optional(), Email(), Length(max=120)])
    medical_conditions = TextAreaField('Medical Conditions', validators=[Optional(), Length(max=500)])
    allergies = TextAreaField('Allergies', validators=[Optional(), Length(max=500)])
    medications = TextAreaField('Medications', validators=[Optional(), Length(max=500)])
    last_checkup_date = DateField('Last Checkup Date', validators=[Optional()])
    next_checkup_date = DateField('Next Checkup Date', validators=[Optional()]) 