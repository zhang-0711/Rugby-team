# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.player import Player, PlayerStats
from app.models.squad import Squad
from app.models.coach import Coach
from app.models.coach_profile import CoachProfile
from app.models.junior_player import JuniorPlayer
from app.models.non_player_member import NonPlayerMember
from app.models.member_assistant import MemberAssistant
from app.models.schedule_assistant import ScheduleAssistant
from app.models.training_record import TrainingRecord
from .training_plan import TrainingPlan, TrainingSession, PlayerAttendance
from .skill_assessment import SkillAssessment
from .message import Message
from .medical_record import MedicalRecord
from .game import Game
from .junior_consent_form import JuniorConsentForm
from .player_profile import PlayerProfile
from .season import Season
from .evaluation import Evaluation
# 为了解决循环导入问题，在这里导入所有模型，这样它们就会在应用启动时被注册 

# 导入其他可能存在的模型
try:
    from app.models.skill_assessment import SkillAssessment
except ImportError:
    pass

try:
    from app.models.match_record import MatchRecord
except ImportError:
    pass

try:
    from app.models.youth_player import YouthPlayer, PlayerPerformance
except ImportError:
    pass 

__all__ = [
    'User',
    'Player',
    'PlayerStats',
    'Squad',
    'Coach',
    'CoachProfile',
    'JuniorPlayer',
    'NonPlayerMember',
    'MemberAssistant',
    'ScheduleAssistant',
    'TrainingRecord',
    'TrainingPlan',
    'TrainingSession',
    'PlayerAttendance',
    'SkillAssessment',
    'Message',
    'MedicalRecord',
    'Game',
    'JuniorConsentForm',
    'PlayerProfile',
    'Season',
    'Evaluation'
]