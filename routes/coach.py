from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.forms.coach import CoachProfileForm, TrainingPlanForm, TrainingSessionForm
from app.models.coach_profile import CoachProfile
from app.models.coach import Coach
from app.models.training_plan import TrainingPlan, TrainingSession
from app.models.squad import Squad
from app.models.player import Player
from app.models.skill_assessment import SkillAssessment
from app.models.user import User
from app.models.game import Game
from app.models.injury import Injury
from datetime import datetime, timedelta
from sqlalchemy import and_, desc, func

bp = Blueprint('coach', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    # 检查用户类型，但避免无限循环重定向
    if current_user.user_type != 'coach':
        flash('Access denied: You must be a coach to access this page', 'danger')
        # 重定向到登录页而不是主页，避免循环
        return redirect(url_for('auth.login'))
    
    # Get squads managed by this coach
    squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    # Get players from managed squads
    squad_ids = [squad.id for squad in squads]
    players = Player.query.filter(Player.squad_id.in_(squad_ids)).all() if squad_ids else []
    
    # Get upcoming events (training sessions, matches, skill assessments)
    upcoming_events = []
    
    # Training sessions
    upcoming_training = TrainingSession.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id,
        TrainingSession.date >= datetime.now().date(),
        TrainingSession.date <= datetime.now().date() + timedelta(days=14)
    ).order_by(TrainingSession.date, TrainingSession.start_time).limit(5).all()
    
    for session in upcoming_training:
        upcoming_events.append({
            'title': f'Training: {session.training_plan.title}',
            'date': session.date,
            'time': session.start_time.strftime('%H:%M') if session.start_time else 'TBD',
            'type': 'training'
        })
    
    # Games for teams managed by coach - using direct SQL to avoid squad_id column issue
    try:
        # Using raw SQL to avoid issues with missing squad_id column
        today = datetime.now().date()
        future_date = today + timedelta(days=14)
        
        match_results = db.session.execute(
            """SELECT id, opponent, match_date, kickoff_time 
               FROM Games 
               WHERE match_date >= :today AND match_date <= :future_date 
               ORDER BY match_date 
               LIMIT 5""",
            {"today": today, "future_date": future_date}
        ).fetchall()
        
        # Convert to a list of dictionaries
        upcoming_matches = []
        for match in match_results:
            upcoming_matches.append({
                'id': match.id,
                'opponent': match.opponent,
                'match_date': match.match_date,
                'kickoff_time': match.kickoff_time
            })
    except Exception as e:
        current_app.logger.error(f"Error fetching upcoming matches: {str(e)}")
        upcoming_matches = []
    
    for match in upcoming_matches:
        upcoming_events.append({
            'title': f'Match vs {match["opponent"]}',
            'date': match["match_date"],
            'time': match["kickoff_time"].strftime('%H:%M') if match["kickoff_time"] else 'TBD',
            'type': 'match'
        })
    
    # Sort events by date
    upcoming_events.sort(key=lambda x: x['date'])
    
    # Get recent activity log
    recent_activities = []
    
    # Recent skill assessments
    recent_assessments = SkillAssessment.query.filter_by(
        coach_id=current_user.id
    ).order_by(desc(SkillAssessment.created_at)).limit(3).all()
    
    for assessment in recent_assessments:
        player_name = ''
        if assessment.player:
            player = User.query.get(Player.query.get(assessment.player_id).user_id)
            player_name = player.name if player else 'Unknown'
        elif assessment.junior_player:
            player_name = assessment.junior_player.name
        
        recent_activities.append({
            'title': f'Skill Assessment: {assessment.skill_type}',
            'description': f'Assessed {player_name}\'s {assessment.skill_type} skills, level: {assessment.skill_level}',
            'timestamp': assessment.created_at,
            'related_to': 'Skill Assessment'
        })
    
    # Recent training sessions
    recent_training = TrainingSession.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id,
        TrainingSession.date < datetime.now().date()
    ).order_by(desc(TrainingSession.date)).limit(3).all()
    
    for session in recent_training:
        recent_activities.append({
            'title': f'Training Session: {session.training_plan.title}',
            'description': f'Conducted training session with focus on {session.focus_area}',
            'timestamp': datetime.combine(session.date, session.start_time) if session.start_time else datetime.combine(session.date, datetime.min.time()),
            'related_to': 'Training'
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:5]  # Limit to 5 most recent activities
    
    return render_template('coach/dashboard.html', 
                          title='Coach Dashboard',
                          squads=squads,
                          upcoming_events=upcoming_events,
                          recent_activities=recent_activities)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    form = CoachProfileForm()
    profile = CoachProfile.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        if profile is None:
            profile = CoachProfile(user_id=current_user.id)
            db.session.add(profile)
        
        profile.specialization = form.specialization.data
        profile.years_of_experience = form.years_of_experience.data
        profile.qualifications = form.qualifications.data
        profile.bio = form.bio.data
        profile.contact_number = form.contact_number.data
        profile.emergency_contact = form.emergency_contact.data
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('coach.profile'))
    
    elif request.method == 'GET' and profile is not None:
        form.specialization.data = profile.specialization
        form.years_of_experience.data = profile.years_of_experience
        form.qualifications.data = profile.qualifications
        form.bio.data = profile.bio
        form.contact_number.data = profile.contact_number
        form.emergency_contact.data = profile.emergency_contact
    
    return render_template('coach/profile.html', title='Coach Profile', form=form)

@bp.route('/players-overview')
@login_required
def players_overview():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
        
    # Get squads managed by this coach - using the same logic as other functions
    all_squads = []
    
    # Method 1: Direct association through Coach model
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id:
        direct_squad = Squad.query.get(coach.squad_id)
        if direct_squad:
            all_squads.append(direct_squad)
    
    # Method 2: Association through TrainingPlan
    plan_squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    # Add squads from training plans (avoiding duplicates)
    for squad in plan_squads:
        if not any(s.id == squad.id for s in all_squads):
            all_squads.append(squad)
            
    squads = all_squads
    
    # Get players for each squad
    squad_players = {}
    for squad in squads:
        players = Player.query.filter_by(squad_id=squad.id).all()
        player_data = []
        for player in players:
            user = User.query.get(player.user_id)
            # 暂时跳过伤病查询，因为injuries表不存在
            player_data.append({
                'id': player.id,
                'user_id': player.user_id,
                'name': user.name,
                'position': player.preferred_positions,
                'injuries': [],  # 提供空列表作为默认值
                'has_health_issues': bool(player.health_issues) if hasattr(player, 'health_issues') else False
            })
        squad_players[squad.id] = player_data
    
    return render_template('coach/players_overview.html',
                         title='Players Overview',
                         squads=squads,
                         squad_players=squad_players)

@bp.route('/skill-assessment')
@login_required
def skill_assessment():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取当前教练所属球队信息
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    
    if not coach:
        flash('Coach profile not found', 'danger')
        return redirect(url_for('coach.dashboard'))
    
    # 获取教练所属球队的球员信息
    squad = coach.squad
    players = []
    
    if squad:
        players = Player.query.filter_by(squad_id=squad.id).all()
        
        # 为每个球员添加用户信息
        for player in players:
            player.user_info = User.query.get(player.user_id)
    
    return render_template('coach/skill_assessment.html', 
                          title='Skill Assessment',
                          squad=squad,
                          players=players)

# skill_charts function and related code removed

@bp.route('/api/squad-players/<int:squad_id>', methods=['GET'])
@login_required
def get_squad_players(squad_id):
    """API endpoint to get all players in a squad"""
    if current_user.user_type != 'coach':
        return jsonify({'error': 'Access denied'}), 403
    
    # Verify the coach has access to this squad
    has_access = False
    
    # Check direct association
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == squad_id:
        has_access = True
    
    # Check training plan association
    if not has_access:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=squad_id
        ).first()
        if training_plan:
            has_access = True
    
    if not has_access:
        return jsonify({'error': 'Not authorized to view this squad'}), 403
    
    # Get all players in the squad
    players = Player.query.filter_by(squad_id=squad_id).all()
    player_list = []
    
    for player in players:
        user = User.query.get(player.user_id)
        player_list.append({
            'id': player.id,
            'name': user.name if user else f'Player #{player.id}'
        })
    
    return jsonify({
        'squad_id': squad_id,
        'players': player_list
    })

@bp.route('/api/player-skills/<int:player_id>', methods=['GET'])
@login_required
def get_player_skills(player_id):
    """API endpoint to get skill data for a specific player"""
    if current_user.user_type != 'coach':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the player
    player = Player.query.get_or_404(player_id)
    
    # Verify the coach has access to this player's squad
    has_access = False
    
    # Check direct association
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == player.squad_id:
        has_access = True
    
    # Check training plan association
    if not has_access and player.squad_id:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=player.squad_id
        ).first()
        if training_plan:
            has_access = True
    
    if not has_access:
        return jsonify({'error': 'Not authorized to view this player'}), 403
    
    # Get player information
    user = User.query.get(player.user_id)
    player_name = user.name if user else f'Player #{player.id}'
    
    # Define the 5 core skills
    core_skills = ['Passing', 'Tackling', 'Kicking', 'Running', 'Teamwork']
    
    # Get the latest assessment for each core skill
    skill_data = {}
    for skill in core_skills:
        # Get the most recent assessment for this skill
        assessment = SkillAssessment.query.filter_by(
            player_id=player_id,
            skill_type=skill
        ).order_by(SkillAssessment.assessment_date.desc()).first()
        
        skill_data[skill] = assessment.skill_level if assessment else 1
    
    return jsonify({
        'player_id': player_id,
        'player_name': player_name,
        'skills': skill_data,
        'core_skills': core_skills
    })

@bp.route('/api/player-detailed-skills/<int:player_id>', methods=['GET'])
@login_required
def get_player_detailed_skills(player_id):
    """API endpoint to get detailed skill breakdown for a player"""
    if current_user.user_type != 'coach':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the player
    player = Player.query.get_or_404(player_id)
    
    # Verify the coach has access to this player's squad
    has_access = False
    
    # Check direct association
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == player.squad_id:
        has_access = True
    
    # Check training plan association
    if not has_access and player.squad_id:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=player.squad_id
        ).first()
        if training_plan:
            has_access = True
    
    if not has_access:
        return jsonify({'error': 'Not authorized to view this player'}), 403
    
    # Define detailed skill breakdowns
    detailed_skills = {
        'Passing': ['Standard', 'Spin', 'Pop'],
        'Tackling': ['Front', 'Rear', 'Side', 'Scrabble'],
        'Kicking': ['Drop', 'Punt', 'Grubber', 'Goal']
    }
    
    # Get the detailed skill assessments
    # In a real implementation, this would come from a detailed_skill_assessments table
    # For now, we'll generate simulated data based on the player's core skill ratings
    
    # First get the core skill ratings
    core_skill_ratings = {}
    for skill in detailed_skills.keys():
        assessment = SkillAssessment.query.filter_by(
            player_id=player_id,
            skill_type=skill
        ).order_by(SkillAssessment.assessment_date.desc()).first()
        
        core_skill_ratings[skill] = assessment.skill_level if assessment else 3  # Default to average if not found
    
    # Now generate detailed ratings that average to the core rating
    detailed_ratings = {}
    for skill, sub_skills in detailed_skills.items():
        core_rating = core_skill_ratings[skill]
        detailed_ratings[skill] = {}
        
        # Generate random ratings around the core rating (within ±1)
        import random
        for sub_skill in sub_skills:
            # Ensure the rating stays within 1-5 range
            min_rating = max(1, core_rating - 1)
            max_rating = min(5, core_rating + 1)
            detailed_ratings[skill][sub_skill] = round(random.uniform(min_rating, max_rating), 1)
    
    return jsonify({
        'player_id': player_id,
        'detailed_skills': detailed_skills,
        'detailed_ratings': detailed_ratings
    })

@bp.route('/api/squad-skills/<int:squad_id>', methods=['GET'])
@login_required
def get_squad_skills(squad_id):
    """API endpoint to get average skill data for an entire squad"""
    if current_user.user_type != 'coach':
        return jsonify({'error': 'Access denied'}), 403
    
    # Verify the coach has access to this squad
    has_access = False
    
    # Check direct association
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == squad_id:
        has_access = True
    
    # Check training plan association
    if not has_access:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=squad_id
        ).first()
        if training_plan:
            has_access = True
    
    if not has_access:
        return jsonify({'error': 'Not authorized to view this squad'}), 403
    
    # Get all players in the squad
    players = Player.query.filter_by(squad_id=squad_id).all()
    player_ids = [player.id for player in players]
    
    # Define the 5 core skills
    core_skills = ['Passing', 'Tackling', 'Kicking', 'Running', 'Teamwork']
    
    # Get average skill levels for the squad
    squad_averages = {}
    for skill in core_skills:
        # Initialize total and count
        total_level = 0
        count = 0
        
        # For each player, get their latest assessment for this skill
        for player_id in player_ids:
            assessment = SkillAssessment.query.filter_by(
                player_id=player_id,
                skill_type=skill
            ).order_by(SkillAssessment.assessment_date.desc()).first()
            
            if assessment:
                total_level += assessment.skill_level
                count += 1
        
        # Calculate average (default to 1 if no assessments)
        squad_averages[skill] = round(total_level / count, 1) if count > 0 else 1
    
    # Get squad info
    squad = Squad.query.get(squad_id)
    squad_name = squad.name if squad else f'Squad #{squad_id}'
    
    return jsonify({
        'squad_id': squad_id,
        'squad_name': squad_name,
        'player_count': len(player_ids),
        'average_skills': squad_averages,
        'core_skills': core_skills
    })

@bp.route('/api/player-squad/<int:player_id>', methods=['GET'])
@login_required
def get_player_squad(player_id):
    """API endpoint to get the squad a player belongs to"""
    if current_user.user_type != 'coach':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the player
    player = Player.query.get_or_404(player_id)
    
    # Verify the coach has access to this player's squad
    has_access = False
    
    # Check direct association
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == player.squad_id:
        has_access = True
    
    # Check training plan association
    if not has_access and player.squad_id:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=player.squad_id
        ).first()
        if training_plan:
            has_access = True
    
    if not has_access:
        return jsonify({'error': 'Not authorized to view this player'}), 403
    
    # Get squad information
    squad = Squad.query.get(player.squad_id) if player.squad_id else None
    
    return jsonify({
        'player_id': player_id,
        'squad_id': player.squad_id,
        'squad_name': squad.name if squad else None
    })

@bp.route('/attendance')
@login_required
def attendance():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get training sessions for this coach
    training_sessions = TrainingSession.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).order_by(TrainingSession.date.desc()).all()
    
    return render_template('coach/attendance.html', 
                         title='Attendance Management',
                         training_sessions=training_sessions)

@bp.route('/matches')
@login_required
def matches():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get squads managed by this coach
    squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    squad_ids = [squad.id for squad in squads]
    
    # Use direct SQL query to avoid ORM issues with missing columns
    try:
        # Using raw SQL to avoid issues with missing squad_id column
        match_results = db.session.execute(
            """SELECT id, opponent, match_date, location, kickoff_time, 
                      score_for, score_against, result, comments_half1, comments_half2
               FROM Games 
               ORDER BY match_date DESC"""
        ).fetchall()
        
        # Convert to a list of dictionaries for easier template rendering
        matches = []
        for match in match_results:
            matches.append({
                'id': match.id,
                'opponent': match.opponent,
                'match_date': match.match_date,
                'location': match.location,
                'kickoff_time': match.kickoff_time,
                'score_for': match.score_for,
                'score_against': match.score_against,
                'result': match.result,
                'comments_half1': match.comments_half1,
                'comments_half2': match.comments_half2
            })
    except Exception as e:
        current_app.logger.error(f"Error fetching matches: {str(e)}")
        flash(f"Error loading match data: {str(e)}", 'danger')
        matches = []
    
    return render_template('coach/matches.html', 
                         title='Match Records',
                         matches=matches,
                         squads=squads,
                         current_date=datetime.now().date())

@bp.route('/notifications')
@login_required
def notifications():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get squads managed by this coach
    squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    return render_template('coach/notifications.html', 
                         title='Send Notifications',
                         squads=squads)

@bp.route('/squads', methods=['GET', 'POST'])
@login_required
def squads():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # 处理POST请求（教练选择管理队伍）
    if request.method == 'POST' and 'squad_id' in request.form:
        squad_id = request.form.get('squad_id')
        
        try:
            # 确保队伍存在
            squad = Squad.query.get(squad_id)
            if not squad:
                flash('Selected team does not exist', 'danger')
                return redirect(url_for('coach.squads'))
            
            # 检查教练是否已有关联
            coach = Coach.query.filter_by(user_id=current_user.id).first()
            
            if not coach:
                # 如果教练记录不存在，创建一个新的
                coach = Coach(user_id=current_user.id, squad_id=squad_id)
                db.session.add(coach)
                flash(f'You have been successfully associated with team {squad.name}', 'success')
            else:
                # 更新现有教练记录
                coach.squad_id = squad_id
                flash(f'Your team has been updated to {squad.name}', 'success')
            
            db.session.commit()
            return redirect(url_for('coach.squad_details', squad_id=squad_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Team association failed: {str(e)}', 'danger')
    
    # 方法1：获取从Coach表直接关联的队伍
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    direct_squad = None
    if coach and coach.squad_id:
        direct_squad = Squad.query.get(coach.squad_id)
    
    # 方法2：获取通过TrainingPlan关联的队伍
    plan_squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    # 合并两种方式获取的队伍（避免重复）
    all_squads = []
    if direct_squad:
        all_squads.append(direct_squad)
    
    # 添加通过训练计划关联的且不与直接关联队伍重复的队伍
    for squad in plan_squads:
        if direct_squad is None or squad.id != direct_squad.id:
            all_squads.append(squad)
    
    # 如果没有发现队伍，检查数据库中是否有队伍可以分配给当前教练
    if not all_squads:
        # 获取所有没有教练的队伍
        unassigned_squads = Squad.query.outerjoin(Coach).filter(Coach.id.is_(None)).all()
        
        # 也可以考虑获取所有队伍作为备选
        all_available_squads = Squad.query.all()
    else:
        unassigned_squads = []
        all_available_squads = []
    
    return render_template('coach/squads.html', 
                           title='My Teams', 
                           squads=all_squads,
                           unassigned_squads=unassigned_squads,
                           all_available_squads=all_available_squads)

@bp.route('/training-plans', methods=['GET', 'POST'])
@login_required
def training_plans():
    if current_user.user_type != 'coach':
        flash('Access denied: You must be a coach to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get squads for the form
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    all_squads = []
    if coach and coach.squad_id:
        direct_squad = Squad.query.get(coach.squad_id)
        if direct_squad:
            all_squads.append(direct_squad)
            
    plan_squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    for squad in plan_squads:
        if not any(s.id == squad.id for s in all_squads):
            all_squads.append(squad)
            
    # Initialize the form for creating a new training plan
    form = TrainingPlanForm()
    form.squad_id.choices = [(s.id, s.name) for s in all_squads]
    
    # Handle form submission
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        frequency = request.form.get('frequency')
        squad_id = request.form.get('squad_id')
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json'
        
        # Parse the manually entered dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y/%m/%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y/%m/%d').date() if end_date_str else None
            
            # Validate form data
            if not title or not start_date or not end_date or not frequency or not squad_id:
                error_msg = 'Please fill in all required fields'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                else:
                    flash(error_msg, 'danger')
            else:
                # Create new training plan
                plan = TrainingPlan(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    coach_id=current_user.id,
                    squad_id=int(squad_id)
                )
                
                db.session.add(plan)
                db.session.commit()
                
                # Generate training sessions based on plan frequency
                generate_training_sessions(plan)
                
                success_msg = 'Training plan created successfully!'
                
                # Get squad name for AJAX response
                squad = Squad.query.get(int(squad_id))
                squad_name = squad.name if squad else ''
                
                if is_ajax:
                    return jsonify({
                        'success': True, 
                        'message': success_msg,
                        'plan': {
                            'id': plan.id,
                            'title': plan.title,
                            'description': plan.description,
                            'start_date': plan.start_date.strftime('%Y-%m-%d'),
                            'end_date': plan.end_date.strftime('%Y-%m-%d'),
                            'frequency': plan.frequency,
                            'squad_id': plan.squad_id,
                            'squad_name': squad_name,
                            'status': 'active'
                        }
                    })
                else:
                    flash(success_msg, 'success')
                    return redirect(url_for('coach.training_plans', success=True, plan_created=True))
        except ValueError:
            error_msg = 'Invalid date format. Please use YYYY/MM/DD format'
            if is_ajax:
                return jsonify({'success': False, 'message': error_msg})
            else:
                flash(error_msg, 'danger')
        
    # Get all training plans for this coach
    plans = TrainingPlan.query.filter_by(coach_id=current_user.id).order_by(TrainingPlan.start_date.desc()).all()
    
    # Get upcoming training sessions
    upcoming_sessions = TrainingSession.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id,
        TrainingSession.date >= datetime.now().date()
    ).order_by(TrainingSession.date, TrainingSession.start_time).limit(5).all()
    
    # Get recent completed training sessions
    recent_sessions = TrainingSession.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id,
        TrainingSession.date < datetime.now().date(),
        TrainingSession.status == 'completed'
    ).order_by(TrainingSession.date.desc()).limit(5).all()
    
    return render_template('coach/training_plans.html',
                          title='Training Management',
                          plans=plans,
                          squads=all_squads,
                          upcoming_sessions=upcoming_sessions,
                          recent_sessions=recent_sessions,
                          form=form)

@bp.route('/squad/<int:squad_id>')
@login_required
def squad_details(squad_id):
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the squad
    squad = Squad.query.get_or_404(squad_id)
    
    # Check if the coach manages this squad (either through direct association or training plan)
    is_authorized = False
    
    # Method 1: Check direct association through Coach model
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == squad_id:
        is_authorized = True
    
    # Method 2: Check association through TrainingPlan
    if not is_authorized:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=squad_id
        ).first()
        
        if training_plan:
            is_authorized = True
    
    # If not authorized, return 404
    if not is_authorized:
        flash('You are not authorized to manage this team', 'danger')
        return redirect(url_for('coach.squads'))
    
    # Get all players in this squad
    players = Player.query.filter_by(squad_id=squad_id).all()
    
    # Get all available players (categorized)
    # 1. Players not assigned to any squad
    unassigned_players = Player.query.filter(Player.squad_id.is_(None)).all()
    
    # 2. Players in other squads (that this coach doesn't manage)
    # First get all squads this coach manages
    managed_squad_ids = db.session.query(Squad.id).join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).all()
    managed_squad_ids = [s[0] for s in managed_squad_ids]
    
    # Then find players in other squads
    other_squad_players = Player.query.join(User).filter(
        Player.squad_id.isnot(None),
        Player.squad_id != squad_id,
        ~Player.squad_id.in_(managed_squad_ids) if managed_squad_ids else False
    ).order_by(User.name).all()
    
    # 3. Players in other squads this coach manages
    other_managed_players = Player.query.join(User).filter(
        Player.squad_id.isnot(None),
        Player.squad_id != squad_id,
        Player.squad_id.in_(managed_squad_ids) if managed_squad_ids else False
    ).order_by(User.name).all()
    
    # Get total available players count
    available_players = unassigned_players + other_squad_players + other_managed_players
    
    # Group available players by their status
    player_categories = {
        'unassigned': unassigned_players,
        'other_squads': other_squad_players,
        'other_managed': other_managed_players
    }
    
    return render_template('coach/squad_details.html', 
                          title=f'Team: {squad.name}',
                          squad=squad,
                          players=players,
                          available_players=available_players,
                          player_categories=player_categories)

@bp.route('/squad/<int:squad_id>/add_player/<int:player_id>', methods=['POST'])
@login_required
def add_player_to_squad(squad_id, player_id):
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the squad
    squad = Squad.query.get_or_404(squad_id)
    
    # Check if the coach manages this squad (either through direct association or training plan)
    is_authorized = False
    
    # Method 1: Check direct association through Coach model
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == squad_id:
        is_authorized = True
    
    # Method 2: Check association through TrainingPlan
    if not is_authorized:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=squad_id
        ).first()
        
        if training_plan:
            is_authorized = True
    
    # If not authorized, return 404
    if not is_authorized:
        flash('You are not authorized to manage this team', 'danger')
        return redirect(url_for('coach.squads'))
    
    # Get the player
    player = Player.query.get_or_404(player_id)
    
    # Get player's current squad (if any)
    old_squad = None
    if player.squad_id is not None:
        old_squad = Squad.query.get(player.squad_id)
        
        # Check if coach has permission to remove player from current squad
        is_coach_of_old_squad = False
        
        # Check through Coach model
        if coach and coach.squad_id == player.squad_id:
            is_coach_of_old_squad = True
            
        # Check through TrainingPlan if not already authorized
        if not is_coach_of_old_squad:
            is_coach_of_old_squad = db.session.query(TrainingPlan).filter(
                TrainingPlan.squad_id == player.squad_id,
                TrainingPlan.coach_id == current_user.id
            ).first() is not None
        
        # If player is in another coach's squad, deny the transfer
        if not is_coach_of_old_squad:
            flash(f'Cannot transfer player from another coach\'s team ({old_squad.name})', 'danger')
            return redirect(url_for('coach.squad_details', squad_id=squad_id))
    
    # Perform the transfer
    old_squad_name = old_squad.name if old_squad else "unassigned players"
    player.squad_id = squad_id
    db.session.commit()
    
    if old_squad:
        flash(f'Player transferred from {old_squad_name} to {squad.name} successfully', 'success')
    else:
        flash(f'Player added to {squad.name} successfully', 'success')
    
    return redirect(url_for('coach.squad_details', squad_id=squad_id))

@bp.route('/squad/<int:squad_id>/remove_player/<int:player_id>', methods=['POST'])
@login_required
def remove_player_from_squad(squad_id, player_id):
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the squad
    squad = Squad.query.get_or_404(squad_id)
    
    # Check if the coach manages this squad (either through direct association or training plan)
    is_authorized = False
    
    # Method 1: Check direct association through Coach model
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == squad_id:
        is_authorized = True
    
    # Method 2: Check association through TrainingPlan
    if not is_authorized:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=squad_id
        ).first()
        
        if training_plan:
            is_authorized = True
    
    # If not authorized, return 404
    if not is_authorized:
        flash('You are not authorized to manage this team', 'danger')
        return redirect(url_for('coach.squads'))
    
    # Get the player
    player = Player.query.get_or_404(player_id)
    
    # Check if player is in this squad
    if player.squad_id != squad_id:
        flash('This player is not in your team', 'warning')
    else:
        # Remove player from squad
        player.squad_id = None
        db.session.commit()
        flash('Player removed from team successfully', 'success')
    
    return redirect(url_for('coach.squad_details', squad_id=squad_id))

@bp.route('/player/<int:player_id>')
@login_required
def player_detail(player_id):
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the player
    player = Player.query.get_or_404(player_id)
    
    # Get the player's user record
    user = User.query.get_or_404(player.user_id)
    
    # Check if the coach is authorized to view this player
    is_authorized = False
    
    # Check if the player is in a squad managed by this coach (either directly or through training plans)
    # Method 1: Coach directly associated with the squad
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    if coach and coach.squad_id == player.squad_id:
        is_authorized = True
    
    # Method 2: Coach has training plans for the squad
    if not is_authorized and player.squad_id:
        training_plan = TrainingPlan.query.filter_by(
            coach_id=current_user.id,
            squad_id=player.squad_id
        ).first()
        
        if training_plan:
            is_authorized = True
    
    if not is_authorized:
        flash('You are not authorized to view this player\'s details', 'danger')
        return redirect(url_for('coach.players_overview'))
    
    # Get the player's squad
    squad = None
    if player.squad_id:
        squad = Squad.query.get(player.squad_id)
    
    # Get injury history
    injuries = Injury.query.filter_by(player_id=player.id).order_by(Injury.report_date.desc()).all()
    
    # Create player data dictionary with all details
    player_data = {
        'id': player.id,
        'name': user.name,
        'sru_number': user.sru_number,
        'dob': user.dob,
        'age': player.age or calculate_age(user.dob) if user.dob else None,
        'address': user.address,
        'tel_number': user.tel_number,
        'mobile_number': user.mobile_number,
        'email': user.email,
        'postcode': user.postcode,
        'preferred_positions': player.preferred_positions,
        'health_issues': player.health_issues,
        'next_of_kin': player.next_of_kin,
        'next_of_kin_relation': player.next_of_kin_relation,
        'next_of_kin_tel': player.next_of_kin_tel,
        'doctor_name': player.doctor_name,
        'doctor_tel': player.doctor_tel,
        'doctor_address': player.doctor_address,
        'squad_name': squad.name if squad else 'Not assigned'
    }
    
    return render_template('coach/player_detail.html',
                          title=f'Player Details: {user.name}',
                          player_data=player_data,
                          injuries=injuries,
                          current_date=datetime.now().date())

def calculate_age(dob):
    """Calculate age based on date of birth"""
    today = datetime.now().date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@bp.route('/training-plan/<int:id>', methods=['GET', 'POST'])
@login_required
def training_plan(id):
    """View and edit a specific training plan"""
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the training plan
    plan = TrainingPlan.query.get_or_404(id)
    
    # Check if this coach owns this plan
    if plan.coach_id != current_user.id:
        flash('You are not authorized to view this training plan', 'danger')
        return redirect(url_for('coach.training_plans'))
    
    # Get all sessions for this plan
    sessions = TrainingSession.query.filter_by(training_plan_id=plan.id).order_by(TrainingSession.date).all()
    
    # Get squad information
    squad = Squad.query.get(plan.squad_id)
    
    # Track attendance stats
    attendance_stats = {
        'total_sessions': len(sessions),
        'completed_sessions': sum(1 for s in sessions if s.status == 'completed'),
        'upcoming_sessions': sum(1 for s in sessions if s.date >= datetime.now().date()),
        'cancelled_sessions': sum(1 for s in sessions if s.status == 'cancelled')
    }
    
    # Get the form for editing the plan
    form = TrainingPlanForm()
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        frequency = request.form.get('frequency')
        squad_id = request.form.get('squad_id')
        
        # Parse the manually entered dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y/%m/%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y/%m/%d').date() if end_date_str else None
            
            # Validate form data
            if not title or not start_date or not end_date or not frequency or not squad_id:
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('coach.training_plan', id=plan.id))
            
            # Update plan with new data
            plan.title = title
            plan.description = description
            plan.start_date = start_date
            plan.end_date = end_date
            plan.frequency = frequency
            plan.squad_id = int(squad_id)
            
            db.session.commit()
            flash('Training plan updated successfully', 'success')
            return redirect(url_for('coach.training_plan', id=plan.id))
        except ValueError:
            flash('Invalid date format. Please use YYYY/MM/DD format', 'danger')
            return redirect(url_for('coach.training_plan', id=plan.id))
    
    # For GET request, populate form with current plan data
    form.title.data = plan.title
    form.description.data = plan.description
    form.frequency.data = plan.frequency
    form.squad_id.data = plan.squad_id
    
    # Get the coach's squads for the form
    coach = Coach.query.filter_by(user_id=current_user.id).first()
    all_squads = []
    if coach and coach.squad_id:
        direct_squad = Squad.query.get(coach.squad_id)
        if direct_squad:
            all_squads.append(direct_squad)
            
    plan_squads = Squad.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id
    ).distinct().all()
    
    for squad in plan_squads:
        if not any(s.id == squad.id for s in all_squads):
            all_squads.append(squad)
            
    form.squad_id.choices = [(s.id, s.name) for s in all_squads]
    
    return render_template('coach/training_plan_detail.html',
                         title=f'Training Plan: {plan.title}',
                         plan=plan,
                         squad=squad,
                         sessions=sessions,
                         attendance_stats=attendance_stats,
                         form=form)

@bp.route('/session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def training_session(session_id):
    """View and record attendance for a training session"""
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the training session
    session = TrainingSession.query.get_or_404(session_id)
    
    # Check if this coach owns this session's plan
    plan = TrainingPlan.query.get(session.training_plan_id)
    if not plan or plan.coach_id != current_user.id:
        flash('You are not authorized to view this training session', 'danger')
        return redirect(url_for('coach.training_plans'))
    
    # Get squad information
    squad = Squad.query.get(plan.squad_id)
    
    # Get players in the squad
    players = Player.query.filter_by(squad_id=squad.id).all()
    player_data = []
    
    for player in players:
        user = User.query.get(player.user_id)
        
        # Check if player already has attendance for this session
        attendance = PlayerAttendance.query.filter_by(
            player_id=player.id,
            session_id=session_id
        ).first()
        
        player_data.append({
            'id': player.id,
            'name': user.name,
            'attendance_status': attendance.status if attendance else None,
            'notes': attendance.notes if attendance else None
        })
    
    # Handle form submission for recording attendance
    if request.method == 'POST':
        # Update session status if provided
        if 'session_status' in request.form:
            session.status = request.form['session_status']
            db.session.commit()
            flash('Session status updated', 'success')
        
        # Record attendance for each player
        for player in players:
            status_key = f'status_{player.id}'
            notes_key = f'notes_{player.id}'
            
            if status_key in request.form:
                # Check if attendance record exists
                attendance = PlayerAttendance.query.filter_by(
                    player_id=player.id,
                    session_id=session_id
                ).first()
                
                if attendance:
                    # Update existing record
                    attendance.status = request.form[status_key]
                    attendance.notes = request.form.get(notes_key, '')
                else:
                    # Create new record
                    attendance = PlayerAttendance(
                        player_id=player.id,
                        session_id=session_id,
                        status=request.form[status_key],
                        notes=request.form.get(notes_key, '')
                    )
                    db.session.add(attendance)
                    
        db.session.commit()
        flash('Attendance recorded successfully', 'success')
        return redirect(url_for('coach.training_session', session_id=session_id))
    
    return render_template('coach/training_session.html',
                         title=f'Training Session: {session.date.strftime("%d %b %Y")}',
                         session=session,
                         plan=plan,
                         squad=squad,
                         players=player_data)

@bp.route('/training-history', methods=['GET'])
@login_required
def training_history():
    """View training history and attendance records"""
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get all completed sessions for this coach
    completed_sessions = TrainingSession.query.join(TrainingPlan).filter(
        TrainingPlan.coach_id == current_user.id,
        TrainingSession.status == 'completed',
        TrainingSession.date < datetime.now().date()
    ).order_by(TrainingSession.date.desc()).all()
    
    # Get attendance summary for each session
    session_data = []
    for session in completed_sessions:
        # Get squad info
        plan = TrainingPlan.query.get(session.training_plan_id)
        squad = Squad.query.get(plan.squad_id) if plan else None
        
        # Get attendance stats
        attendance_records = PlayerAttendance.query.filter_by(session_id=session.id).all()
        total_players = len(attendance_records) if attendance_records else 0
        present_count = sum(1 for a in attendance_records if a.status == 'present')
        absent_count = sum(1 for a in attendance_records if a.status == 'absent')
        excused_count = sum(1 for a in attendance_records if a.status == 'excused')
        
        # Add to data list
        session_data.append({
            'id': session.id,
            'date': session.date,
            'time': f"{session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}",
            'plan_title': plan.title if plan else 'Unknown',
            'squad_name': squad.name if squad else 'Unknown',
            'total_players': total_players,
            'present_count': present_count,
            'absent_count': absent_count,
            'excused_count': excused_count,
            'attendance_rate': round(present_count / total_players * 100) if total_players > 0 else 0
        })
    
    return render_template('coach/training_history.html',
                         title='Training History',
                         sessions=session_data)

@bp.route('/schedule')
@login_required
def schedule():
    if current_user.user_type != 'coach':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get upcoming training sessions
    today = datetime.now().date()
    sessions = TrainingSession.query.join(TrainingPlan).filter(
        and_(
            TrainingPlan.coach_id == current_user.id,
            TrainingSession.date >= today
        )
    ).order_by(TrainingSession.date, TrainingSession.start_time).all()
    
    return render_template('coach/schedule.html',
                         title='Coach Schedule',
                         sessions=sessions)

def generate_training_sessions(plan):
    """Generate training sessions based on plan frequency"""
    start_date = plan.start_date
    end_date = plan.end_date
    frequency = plan.frequency
    
    current_date = start_date
    while current_date <= end_date:
        session = TrainingSession(
            date=current_date,
            start_time=datetime.strptime('09:00', '%H:%M').time(),
            end_time=datetime.strptime('11:00', '%H:%M').time(),
            plan_id=plan.id
        )
        db.session.add(session)
        
        # Increment date based on frequency
        if frequency == 'weekly':
            current_date += timedelta(days=7)
        elif frequency == 'biweekly':
            current_date += timedelta(days=14)
        elif frequency == 'monthly':
            # Add one month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    db.session.commit() 