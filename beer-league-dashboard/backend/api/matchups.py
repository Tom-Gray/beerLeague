from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import desc
import json
from models import Team, Matchup, WeeklyResult
from database import get_db

api = Namespace('matchups', description='Bench scoring matchup operations')

def get_bench_players_for_team(session, roster_id, week):
    """Get bench player details for a team in a specific week."""
    weekly_result = session.query(WeeklyResult).filter_by(
        roster_id=roster_id, 
        week=week
    ).first()
    
    if not weekly_result or not weekly_result.bench_players_json:
        return []
    
    try:
        # Parse the JSON string to get player details
        players_data = json.loads(weekly_result.bench_players_json)
        return players_data if isinstance(players_data, list) else []
    except (json.JSONDecodeError, TypeError):
        return []

# Response models
bench_player_model = api.model('BenchPlayer', {
    'player_id': fields.String(required=True, description='Player ID'),
    'name': fields.String(required=True, description='Player name'),
    'position': fields.String(required=True, description='Player position'),
    'team': fields.String(required=True, description='NFL team'),
    'points': fields.Float(required=True, description='Points scored')
})

matchup_team_model = api.model('MatchupTeam', {
    'roster_id': fields.Integer(required=True, description='Team roster ID'),
    'team_name': fields.String(required=True, description='Team name'),
    'bench_points': fields.Float(required=True, description='Bench points scored'),
    'bench_players': fields.List(fields.Nested(bench_player_model), description='Individual bench player details')
})

matchup_model = api.model('Matchup', {
    'id': fields.Integer(required=True, description='Matchup ID'),
    'week': fields.Integer(required=True, description='Week number'),
    'matchup_id': fields.Integer(required=True, description='Sleeper matchup ID'),
    'team1': fields.Nested(matchup_team_model),
    'team2': fields.Nested(matchup_team_model),
    'winner': fields.Nested(matchup_team_model, allow_null=True),
    'margin_of_victory': fields.Float(description='Point margin of victory'),
    'date_recorded': fields.DateTime(description='Date when matchup was recorded')
})

@api.route('/')
class MatchupList(Resource):
    @api.marshal_list_with(matchup_model)
    def get(self):
        """Get all bench scoring matchups"""
        week = request.args.get('week', type=int)
        
        session = next(get_db())
        try:
            query = session.query(Matchup)
            
            if week:
                query = query.filter(Matchup.week == week)
            
            matchups = query.order_by(desc(Matchup.week), Matchup.matchup_id).all()
            
            result = []
            for matchup in matchups:
                # Get team details
                team1 = session.query(Team).filter_by(roster_id=matchup.team1_roster_id).first()
                team2 = session.query(Team).filter_by(roster_id=matchup.team2_roster_id).first()
                winner = None
                
                # Get bench player details for both teams
                team1_bench_players = get_bench_players_for_team(session, matchup.team1_roster_id, matchup.week)
                team2_bench_players = get_bench_players_for_team(session, matchup.team2_roster_id, matchup.week)
                
                if matchup.winner_roster_id:
                    winner = session.query(Team).filter_by(roster_id=matchup.winner_roster_id).first()
                    winner_bench_players = team1_bench_players if winner.roster_id == matchup.team1_roster_id else team2_bench_players
                
                result.append({
                    'id': matchup.id,
                    'week': matchup.week,
                    'matchup_id': matchup.matchup_id,
                    'team1': {
                        'roster_id': team1.roster_id,
                        'team_name': team1.team_name,
                        'bench_points': matchup.team1_bench_points,
                        'bench_players': team1_bench_players
                    },
                    'team2': {
                        'roster_id': team2.roster_id,
                        'team_name': team2.team_name,
                        'bench_points': matchup.team2_bench_points,
                        'bench_players': team2_bench_players
                    },
                    'winner': {
                        'roster_id': winner.roster_id,
                        'team_name': winner.team_name,
                        'bench_points': matchup.team1_bench_points if winner.roster_id == matchup.team1_roster_id else matchup.team2_bench_points,
                        'bench_players': winner_bench_players
                    } if winner else None,
                    'margin_of_victory': matchup.margin_of_victory,
                    'date_recorded': matchup.date_recorded
                })
            
            return result
            
        finally:
            session.close()

@api.route('/week/<int:week>')
class WeeklyMatchups(Resource):
    @api.marshal_list_with(matchup_model)
    def get(self, week):
        """Get matchups for a specific week"""
        session = next(get_db())
        try:
            matchups = session.query(Matchup).filter_by(week=week).order_by(Matchup.matchup_id).all()
            
            result = []
            for matchup in matchups:
                # Get team details
                team1 = session.query(Team).filter_by(roster_id=matchup.team1_roster_id).first()
                team2 = session.query(Team).filter_by(roster_id=matchup.team2_roster_id).first()
                winner = None
                
                # Get bench player details for both teams
                team1_bench_players = get_bench_players_for_team(session, matchup.team1_roster_id, matchup.week)
                team2_bench_players = get_bench_players_for_team(session, matchup.team2_roster_id, matchup.week)
                
                if matchup.winner_roster_id:
                    winner = session.query(Team).filter_by(roster_id=matchup.winner_roster_id).first()
                    winner_bench_players = team1_bench_players if winner.roster_id == matchup.team1_roster_id else team2_bench_players
                
                result.append({
                    'id': matchup.id,
                    'week': matchup.week,
                    'matchup_id': matchup.matchup_id,
                    'team1': {
                        'roster_id': team1.roster_id,
                        'team_name': team1.team_name,
                        'bench_points': matchup.team1_bench_points,
                        'bench_players': team1_bench_players
                    },
                    'team2': {
                        'roster_id': team2.roster_id,
                        'team_name': team2.team_name,
                        'bench_points': matchup.team2_bench_points,
                        'bench_players': team2_bench_players
                    },
                    'winner': {
                        'roster_id': winner.roster_id,
                        'team_name': winner.team_name,
                        'bench_points': matchup.team1_bench_points if winner.roster_id == matchup.team1_roster_id else matchup.team2_bench_points,
                        'bench_players': winner_bench_players
                    } if winner else None,
                    'margin_of_victory': matchup.margin_of_victory,
                    'date_recorded': matchup.date_recorded
                })
            
            return result
            
        finally:
            session.close()

@api.route('/team/<int:roster_id>')
class TeamMatchups(Resource):
    @api.marshal_list_with(matchup_model)
    def get(self, roster_id):
        """Get all matchups for a specific team"""
        session = next(get_db())
        try:
            # Check if team exists
            team = session.query(Team).filter_by(roster_id=roster_id).first()
            if not team:
                api.abort(404, f"Team with roster_id {roster_id} not found")
            
            matchups = session.query(Matchup).filter(
                (Matchup.team1_roster_id == roster_id) |
                (Matchup.team2_roster_id == roster_id)
            ).order_by(desc(Matchup.week)).all()
            
            result = []
            for matchup in matchups:
                # Get team details
                team1 = session.query(Team).filter_by(roster_id=matchup.team1_roster_id).first()
                team2 = session.query(Team).filter_by(roster_id=matchup.team2_roster_id).first()
                winner = None
                
                # Get bench player details for both teams
                team1_bench_players = get_bench_players_for_team(session, matchup.team1_roster_id, matchup.week)
                team2_bench_players = get_bench_players_for_team(session, matchup.team2_roster_id, matchup.week)
                
                if matchup.winner_roster_id:
                    winner = session.query(Team).filter_by(roster_id=matchup.winner_roster_id).first()
                    winner_bench_players = team1_bench_players if winner.roster_id == matchup.team1_roster_id else team2_bench_players
                
                result.append({
                    'id': matchup.id,
                    'week': matchup.week,
                    'matchup_id': matchup.matchup_id,
                    'team1': {
                        'roster_id': team1.roster_id,
                        'team_name': team1.team_name,
                        'bench_points': matchup.team1_bench_points,
                        'bench_players': team1_bench_players
                    },
                    'team2': {
                        'roster_id': team2.roster_id,
                        'team_name': team2.team_name,
                        'bench_points': matchup.team2_bench_points,
                        'bench_players': team2_bench_players
                    },
                    'winner': {
                        'roster_id': winner.roster_id,
                        'team_name': winner.team_name,
                        'bench_points': matchup.team1_bench_points if winner.roster_id == matchup.team1_roster_id else matchup.team2_bench_points,
                        'bench_players': winner_bench_players
                    } if winner else None,
                    'margin_of_victory': matchup.margin_of_victory,
                    'date_recorded': matchup.date_recorded
                })
            
            return result
            
        finally:
            session.close()

@api.route('/head-to-head/<int:team1_id>/<int:team2_id>')
class HeadToHeadMatchups(Resource):
    def get(self, team1_id, team2_id):
        """Get head-to-head matchup history between two teams"""
        session = next(get_db())
        try:
            # Check if both teams exist
            team1 = session.query(Team).filter_by(roster_id=team1_id).first()
            team2 = session.query(Team).filter_by(roster_id=team2_id).first()
            
            if not team1:
                api.abort(404, f"Team with roster_id {team1_id} not found")
            if not team2:
                api.abort(404, f"Team with roster_id {team2_id} not found")
            
            # Get all matchups between these teams
            matchups = session.query(Matchup).filter(
                ((Matchup.team1_roster_id == team1_id) & (Matchup.team2_roster_id == team2_id)) |
                ((Matchup.team1_roster_id == team2_id) & (Matchup.team2_roster_id == team1_id))
            ).order_by(desc(Matchup.week)).all()
            
            # Calculate head-to-head record
            team1_wins = 0
            team2_wins = 0
            total_team1_points = 0
            total_team2_points = 0
            
            matchup_details = []
            for matchup in matchups:
                # Determine which team is which in this matchup
                if matchup.team1_roster_id == team1_id:
                    team1_points = matchup.team1_bench_points
                    team2_points = matchup.team2_bench_points
                else:
                    team1_points = matchup.team2_bench_points
                    team2_points = matchup.team1_bench_points
                
                total_team1_points += team1_points
                total_team2_points += team2_points
                
                if matchup.winner_roster_id == team1_id:
                    team1_wins += 1
                elif matchup.winner_roster_id == team2_id:
                    team2_wins += 1
                
                matchup_details.append({
                    'week': matchup.week,
                    'team1_points': team1_points,
                    'team2_points': team2_points,
                    'winner_id': matchup.winner_roster_id,
                    'margin': matchup.margin_of_victory,
                    'date_recorded': matchup.date_recorded.isoformat()
                })
            
            return {
                'team1': {
                    'roster_id': team1.roster_id,
                    'team_name': team1.team_name,
                    'wins': team1_wins,
                    'total_points': total_team1_points,
                    'avg_points': total_team1_points / len(matchups) if matchups else 0
                },
                'team2': {
                    'roster_id': team2.roster_id,
                    'team_name': team2.team_name,
                    'wins': team2_wins,
                    'total_points': total_team2_points,
                    'avg_points': total_team2_points / len(matchups) if matchups else 0
                },
                'total_matchups': len(matchups),
                'matchups': matchup_details
            }
            
        finally:
            session.close()
