"""
Member Assistant Service for Simply Rugby.
This module provides functionality for managing games, venues, and scheduling.
"""
from app import db
from app.models.game import Game
from app.models.venue import Venue
from app.models.season import Season
from app.models.squad import Squad
from app.models.user import User
from app.models.player import Player
from app.models.junior_player import JuniorPlayer
from app.models.coach import Coach
from app.models.message import Message
from datetime import datetime, timedelta
import calendar


class MemberAssistantService:
    """
    Service for managing games, venues, and scheduling for member assistants.
    """
    
    @staticmethod
    def get_current_season():
        """
        Get the current active season.
        
        Returns:
            Season: The current active season or None if not found
        """
        current_date = datetime.now().date()
        
        # Try to find a season that includes the current date
        season = Season.query.filter(
            Season.start_date <= current_date,
            Season.end_date >= current_date
        ).first()
        
        # If no current season, get the most recent one
        if not season:
            season = Season.query.order_by(Season.end_date.desc()).first()
            
        return season
    
    @staticmethod
    def get_all_seasons():
        """
        Get all seasons ordered by start date descending.
        
        Returns:
            list: List of Season objects
        """
        return Season.query.order_by(Season.start_date.desc()).all()
    
    @staticmethod
    def create_season(name, start_date, end_date):
        """
        Create a new season.
        
        Args:
            name (str): Season name
            start_date (date): Season start date
            end_date (date): Season end date
            
        Returns:
            Season: The newly created season
        """
        try:
            season = Season(
                name=name,
                start_date=start_date,
                end_date=end_date,
                status='not_started'
            )
            
            db.session.add(season)
            db.session.commit()
            return season
        except Exception as e:
            db.session.rollback()
            print(f"Error creating season: {str(e)}")
            return None
    
    @staticmethod
    def get_all_venues():
        """
        Get all venues.
        
        Returns:
            list: List of Venue objects
        """
        return Venue.query.all()
    
    @staticmethod
    def create_venue(name, address, capacity, facilities, is_home, contact_info, notes):
        """
        Create a new venue.
        
        Args:
            name (str): Venue name
            address (str): Venue address
            capacity (int): Venue capacity
            facilities (str): Available facilities
            is_home (bool): Whether it's a home venue
            contact_info (str): Contact information
            notes (str): Additional notes
            
        Returns:
            Venue: The newly created venue
        """
        try:
            venue = Venue(
                name=name,
                address=address,
                capacity=capacity,
                facilities=facilities,
                is_home=is_home,
                contact_info=contact_info,
                notes=notes
            )
            
            db.session.add(venue)
            db.session.commit()
            return venue
        except Exception as e:
            db.session.rollback()
            print(f"Error creating venue: {str(e)}")
            return None
    
    @staticmethod
    def get_upcoming_games(limit=10):
        """
        Get upcoming games.
        
        Args:
            limit (int): Maximum number of games to return
            
        Returns:
            list: List of upcoming Game objects
        """
        current_date = datetime.now().date()
        
        return Game.query.filter(
            Game.match_date >= current_date
        ).order_by(Game.match_date.asc()).limit(limit).all()
    
    @staticmethod
    def get_previous_games(limit=10):
        """
        Get previous games.
        
        Args:
            limit (int): Maximum number of games to return
            
        Returns:
            list: List of previous Game objects
        """
        current_date = datetime.now().date()
        
        return Game.query.filter(
            Game.match_date < current_date
        ).order_by(Game.match_date.desc()).limit(limit).all()
    
    @staticmethod
    def create_game(season_id, opponent, match_date, kickoff_time, location, notes=None):
        """
        Create a new game.
        
        Args:
            season_id (int): Season ID
            opponent (str): Opponent name
            match_date (date): Match date
            kickoff_time (time): Kickoff time
            location (str): Location (home/away)
            notes (str): Additional notes
            
        Returns:
            Game: The newly created game
        """
        try:
            game = Game(
                season_id=season_id,
                opponent=opponent,
                match_date=match_date,
                kickoff_time=kickoff_time,
                location=location,
                comments_half1=notes
            )
            
            db.session.add(game)
            db.session.commit()
            return game
        except Exception as e:
            db.session.rollback()
            print(f"Error creating game: {str(e)}")
            return None
    
    @staticmethod
    def update_game_result(game_id, score_for, score_against, result, comments_half1=None, comments_half2=None):
        """
        Update game result.
        
        Args:
            game_id (int): Game ID
            score_for (int): Team score
            score_against (int): Opponent score
            result (str): Game result (won/lost/drew)
            comments_half1 (str): First half comments
            comments_half2 (str): Second half comments
            
        Returns:
            bool: Success status
        """
        try:
            game = Game.query.get(game_id)
            
            if not game:
                return False
                
            game.score_for = score_for
            game.score_against = score_against
            game.result = result
            
            if comments_half1:
                game.comments_half1 = comments_half1
            if comments_half2:
                game.comments_half2 = comments_half2
                
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating game result: {str(e)}")
            return False
    
    @staticmethod
    def get_calendar_events(year, month):
        """
        Get calendar events for a specific month.
        
        Args:
            year (int): Year
            month (int): Month
            
        Returns:
            dict: Calendar events by day
        """
        # Get the first and last day of the month
        first_day = datetime(year, month, 1).date()
        
        # Get the last day of the month
        if month == 12:
            last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Get all games in this month
        games = Game.query.filter(
            Game.match_date >= first_day,
            Game.match_date <= last_day
        ).all()
        
        # Create a calendar with events
        cal = calendar.monthcalendar(year, month)
        events = {}
        
        # Add games to the calendar
        for game in games:
            day = game.match_date.day
            if day not in events:
                events[day] = []
            
            events[day].append({
                'type': 'game',
                'id': game.id,
                'title': f"vs {game.opponent}",
                'location': game.location,
                'time': game.kickoff_time.strftime('%H:%M') if game.kickoff_time else 'TBD'
            })
        
        return {
            'calendar': cal,
            'events': events,
            'month_name': calendar.month_name[month],
            'year': year
        }
    
    @staticmethod
    def get_squads():
        """
        Get all squads.
        
        Returns:
            list: List of Squad objects
        """
        return Squad.query.all()
    
    @staticmethod
    def get_squad_members(squad_id):
        """
        Get all members of a squad.
        
        Args:
            squad_id (int): Squad ID
            
        Returns:
            dict: Dictionary with players and coaches
        """
        # Get adult players in the squad
        players = Player.query.filter_by(squad_id=squad_id).all()
        
        # Get junior players in the squad
        junior_players = JuniorPlayer.query.filter_by(squad_id=squad_id).all()
        
        # Get user information for each player
        player_users = []
        for player in players:
            user = User.query.get(player.user_id)
            if user:
                player_users.append({
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'type': 'Adult Player',
                    'player_id': player.id
                })
                
        # Get user information for each junior player
        for junior in junior_players:
            user = User.query.get(junior.user_id)
            if user:
                player_users.append({
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'type': 'Junior Player',
                    'player_id': junior.id
                })
        
        # Get coaches associated with the squad
        coaches = []
        squad_coaches = Coach.query.filter_by(squad_id=squad_id).all()
        
        for coach in squad_coaches:
            user = User.query.get(coach.user_id)
            if user:
                coaches.append({
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'coach_id': coach.id
                })
        
        return {
            'players': player_users,
            'coaches': coaches
        }
