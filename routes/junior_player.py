from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.forms.junior_player import JuniorPlayerForm
from app.forms.assessment import SkillAssessmentForm, MatchRecordForm
from app.models.junior_player import JuniorPlayer
from app.models.skill_assessment import SkillAssessment
from app.models.match_record import MatchRecord
from datetime import datetime, timedelta

bp = Blueprint('junior_player', __name__, url_prefix='/junior_player')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'junior_player':
        flash('Access denied: This area is only for junior players.', 'danger')
        # Redirect to login page instead of home to avoid loops
        return redirect(url_for('auth.login'))
    
    player = JuniorPlayer.query.filter_by(user_id=current_user.id).first()
    if not player:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('junior_player.profile'))
    
    # Define the three core skills we want to display
    skill_categories = ['Passing', 'Tackling', 'Kicking']
    
    # Initialize skill assessment data structure
    skills = {}
    last_assessment_date = None
    has_assessment_data = False
    
    # Print debug information
    print(f"DEBUG: Junior player ID = {player.id}")
    
    # Query the latest assessment for each skill category
    for category in skill_categories:
        try:
            assessment = SkillAssessment.query.filter_by(
                junior_player_id=player.id,
                skill_type=category
            ).order_by(SkillAssessment.assessment_date.desc()).first()
            
            print(f"DEBUG: Query for {category} assessment returned: {assessment}")
            
            if assessment:
                skills[category] = assessment.skill_level
                has_assessment_data = True
                
                # Update the latest assessment date
                if not last_assessment_date or assessment.assessment_date > last_assessment_date:
                    last_assessment_date = assessment.assessment_date
            else:
                skills[category] = 3  # Default middle value if no assessment exists
        except Exception as e:
            print(f"ERROR querying {category} assessment: {str(e)}")
            skills[category] = 3  # Default value on error
    
    # Get detailed sub-skills assessments
    detailed_skills = {
        'passing': {
            'Standard': 3,
            'Spin': 2,
            'Pop': 3
        },
        'tackling': {
            'Front': 4,
            'Rear': 2,
            'Side': 3,
            'Scrabble': 2
        },
        'kicking': {
            'Drop': 3,
            'Punt': 4,
            'Grubber': 2,
            'Goal': 3
        }
    }
    
    # Query the latest assessment for each sub-skill
    for skill_type, sub_skills in detailed_skills.items():
        for sub_skill in sub_skills.keys():
            try:
                assessment = SkillAssessment.query.filter_by(
                    junior_player_id=player.id,
                    skill_type=skill_type.capitalize(),
                    sub_skill=sub_skill
                ).order_by(SkillAssessment.assessment_date.desc()).first()
                
                if assessment:
                    detailed_skills[skill_type][sub_skill] = assessment.skill_level
                    has_assessment_data = True
            except Exception as e:
                print(f"ERROR querying {skill_type}.{sub_skill} assessment: {str(e)}")
                # Keep default value on error
    
    if not has_assessment_data:
        print("DEBUG: No assessment data found, using default values for display")
        # If no actual assessment data exists, we'll still use our default values
        # to ensure the radar charts render properly
        if not last_assessment_date:
            last_assessment_date = datetime.now().date()
    
    # Add sample data for upcoming matches
    today = datetime.now().date()
    upcoming_matches = [
        {
            'id': 1,
            'opponent': 'Edinburgh Junior RFC',
            'match_date': today + timedelta(days=7),  # Next week
            'location': 'Home Field, Glasgow',
            'is_home_game': True
        },
        {
            'id': 2,
            'opponent': 'Aberdeen Young Warriors',
            'match_date': today + timedelta(days=14),  # Two weeks from now
            'location': 'Aberdeen Sports Ground',
            'is_home_game': False
        },
        {
            'id': 3,
            'opponent': 'Falkirk Junior Rugby',
            'match_date': today + timedelta(days=21),  # Three weeks from now
            'location': 'Home Field, Glasgow',
            'is_home_game': True
        }
    ]
    
    # Add sample data for recent injuries
    recent_injuries = [
        {
            'id': 1,
            'injury_type': 'Ankle Sprain',
            'report_date': today - timedelta(days=30),
            'severity': 'Moderate',
            'recovery_status': 'Recovering',
            'recovery_time_estimate': 45
        },
        {
            'id': 2,
            'injury_type': 'Shoulder Contusion',
            'report_date': today - timedelta(days=15),
            'severity': 'Mild',
            'recovery_status': 'Almost Healed',
            'recovery_time_estimate': 21
        }
    ]
    
    # Create sample training sessions data
    upcoming_training = [
        {
            'id': 1,
            'date': today + timedelta(days=3),  # 3 days from now
            'time': '16:00 - 18:00',
            'location': 'Training Ground A',
            'focus': 'Passing and Tackling Drills'
        },
        {
            'id': 2,
            'date': today + timedelta(days=5),  # 5 days from now
            'time': '15:30 - 17:30',
            'location': 'Indoor Facility',
            'focus': 'Game Strategy and Fitness'
        }
    ]
    
    return render_template('junior_player/dashboard.html', 
                           title='Dashboard', 
                           player=player,
                           skills=skills,
                           detailed_skills=detailed_skills,
                           has_assessment_data=has_assessment_data,
                           last_assessment_date=last_assessment_date,
                           upcoming_matches=upcoming_matches,
                           recent_injuries=recent_injuries,
                           upcoming_training=upcoming_training)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.user_type != 'junior_player':
        flash('Access denied: This area is only for junior players.', 'danger')
        # 重定向到登录页而不是主页，避免循环
        return redirect(url_for('auth.login'))
        
    form = JuniorPlayerForm()
    player = JuniorPlayer.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        if player is None:
            player = JuniorPlayer(user_id=current_user.id)
            db.session.add(player)
        
        player.sru_number = form.sru_number.data
        player.date_of_birth = form.date_of_birth.data
        player.position = form.position.data
        player.jersey_number = form.jersey_number.data
        player.height = form.height.data
        player.weight = form.weight.data
        player.preferred_foot = form.preferred_foot.data
        player.medical_conditions = form.medical_conditions.data
        player.emergency_contact = form.emergency_contact.data
        player.emergency_phone = form.emergency_phone.data
        player.guardian_consent_signed = form.guardian_consent_signed.data
        player.guardian_consent_date = form.guardian_consent_date.data
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('junior_player.profile'))
    
    elif request.method == 'GET' and player is not None:
        form.sru_number.data = player.sru_number
        form.date_of_birth.data = player.date_of_birth
        form.position.data = player.position
        form.jersey_number.data = player.jersey_number
        form.height.data = player.height
        form.weight.data = player.weight
        form.preferred_foot.data = player.preferred_foot
        form.medical_conditions.data = player.medical_conditions
        form.emergency_contact.data = player.emergency_contact
        form.emergency_phone.data = player.emergency_phone
        form.guardian_consent_signed.data = player.guardian_consent_signed
        form.guardian_consent_date.data = player.guardian_consent_date
    
    return render_template('junior_player/profile.html', title='Junior Player Profile', form=form)

@bp.route('/guardians')
@login_required
def guardians():
    if current_user.user_type != 'junior_player':
        flash('Access denied: This area is only for junior players.', 'danger')
        # 重定向到登录页而不是主页，避免循环
        return redirect(url_for('auth.login'))
    
    player = JuniorPlayer.query.filter_by(user_id=current_user.id).first()
    if not player:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('junior_player.profile'))
    
    return render_template('junior_player/guardians.html',
                         title='Guardians',
                         player=player)

@bp.route('/medical')
@login_required
def medical():
    if current_user.user_type != 'junior_player':
        flash('Access denied: This area is only for junior players.', 'danger')
        # 重定向到登录页而不是主页，避免循环
        return redirect(url_for('auth.login'))
    
    player = JuniorPlayer.query.filter_by(user_id=current_user.id).first()
    if not player:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('junior_player.profile'))
    
    return render_template('junior_player/medical.html',
                           title='Medical Information',
                           player=player)

@bp.route('/skills')
@login_required
def skills():
    if current_user.user_type != 'junior_player':
        flash('Access denied: This area is only for junior players.', 'danger')
        # 重定向到登录页而不是主页，避免循环
        return redirect(url_for('auth.login'))
    
    player = JuniorPlayer.query.filter_by(user_id=current_user.id).first()
    if not player:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('junior_player.profile'))
    
    assessments = SkillAssessment.query.filter_by(junior_player_id=player.id).all()
    
    # Prepare data for ECharts
    skill_data = {}
    for assessment in assessments:
        if assessment.skill_type not in skill_data:
            skill_data[assessment.skill_type] = []
        skill_data[assessment.skill_type].append({
            'date': assessment.assessment_date.strftime('%Y-%m-%d'),
            'level': assessment.skill_level
        })
    
    return render_template('junior_player/skills.html',
                         title='Skill Assessments',
                         assessments=assessments,
                         skill_data=skill_data)

@bp.route('/matches')
@login_required
def matches():
    if current_user.user_type != 'junior_player':
        flash('Access denied: This area is only for junior players.', 'danger')
        # 重定向到登录页而不是主页，避免循环
        return redirect(url_for('auth.login'))
    
    player = JuniorPlayer.query.filter_by(user_id=current_user.id).first()
    if not player:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('junior_player.profile'))
    
    matches = MatchRecord.query.filter_by(junior_player_id=player.id).order_by(
        MatchRecord.match_date.desc()
    ).all()
    
    return render_template('junior_player/matches.html',
                         title='Match Records',
                         matches=matches) 