from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from models import Team, WeeklyResult, Matchup
from database import get_db

api = Namespace('standings', description='Bench scoring standings operations')

# Response models
team_model = api.model('Team', {
    'roster_id': fields.Integer(required=True, description='Team roster ID'),
    'team_name': fields.String(required=True, description='Team name'),
    'owner_id': fields.String(description='Owner ID')
})

standings_entry_model = api.model('StandingsEntry', {
    'team': fields.Nested(team_model),
    'total_points': fields.Float(description='Total bench points'),
    'average_points': fields.Float(description='Average bench points per week'),
    'weeks_played': fields.Integer(description='Number of weeks played'),
    'best_week': fields.Float(description='Best single week performance'),
    'worst_week': fields.Float(description='Worst single week performance'),
    'wins': fields.Integer(description='Number of bench matchup wins'),
    'losses': fields.Integer(description='Number of bench matchup losses'),
    'win_percentage': fields.Float(description='Win percentage')
})

weekly_result_model = api.model('WeeklyResult', {
    'week': fields.Integer(required=True, description='Week number'),
    'roster_id': fields.Integer(required=True, description='Team roster ID'),
    'team_name': fields.String(description='Team name'),
    'total_bench_points': fields.Float(description='Total bench points for the week'),
    'bench_player_count': fields.Integer(description='Number of bench players'),
    'date_recorded': fields.DateTime(description='Date when data was recorded')
})

@api.route('/season')
class SeasonStandings(Resource):
    @api.marshal_list_with(standings_entry_model)
    def get(self):
        """Get season-long bench scoring standings"""
        session = next(get_db())
        try:
            # Get aggregated stats for each team
            team_stats = session.query(
                Team,
                func.sum(WeeklyResult.total_bench_points).label('total_points'),
                func.avg(WeeklyResult.total_bench_points).label('average_points'),
                func.count(WeeklyResult.week).label('weeks_played'),
                func.max(WeeklyResult.total_bench_points).label('best_week'),
                func.min(WeeklyResult.total_bench_points).label('worst_week')
            ).join(WeeklyResult).group_by(Team.roster_id).all()
            
            # Get win/loss records
            standings = []
            for team, total_points, avg_points, weeks_played, best_week, worst_week in team_stats:
                # Calculate wins and losses
                wins = session.query(Matchup).filter(
                    Matchup.winner_roster_id == team.roster_id
                ).count()
                
                total_matchups = session.query(Matchup).filter(
                    (Matchup.team1_roster_id == team.roster_id) |
                    (Matchup.team2_roster_id == team.roster_id)
                ).count()
                
                losses = total_matchups - wins
                win_percentage = wins / total_matchups if total_matchups > 0 else 0
                
                standings.append({
                    'team': {
                        'roster_id': team.roster_id,
                        'team_name': team.team_name,
                        'owner_id': team.owner_id
                    },
                    'total_points': float(total_points or 0),
                    'average_points': float(avg_points or 0),
                    'weeks_played': weeks_played,
                    'best_week': float(best_week or 0),
                    'worst_week': float(worst_week or 0),
                    'wins': wins,
                    'losses': losses,
                    'win_percentage': round(win_percentage, 3)
                })
            
            # Sort by total points descending
            standings.sort(key=lambda x: x['total_points'], reverse=True)
            return standings
            
        finally:
            session.close()

@api.route('/weekly')
class WeeklyStandings(Resource):
    @api.marshal_list_with(weekly_result_model)
    def get(self):
        """Get weekly bench scoring results"""
        week = request.args.get('week', type=int)
        
        session = next(get_db())
        try:
            query = session.query(WeeklyResult).join(Team)
            
            if week:
                query = query.filter(WeeklyResult.week == week)
            
            results = query.order_by(desc(WeeklyResult.total_bench_points)).all()
            
            return [{
                'week': result.week,
                'roster_id': result.roster_id,
                'team_name': result.team.team_name,
                'total_bench_points': result.total_bench_points,
                'bench_player_count': result.bench_player_count,
                'date_recorded': result.date_recorded
            } for result in results]
            
        finally:
            session.close()

@api.route('/team/<int:roster_id>')
class TeamStandings(Resource):
    def get(self, roster_id):
        """Get detailed standings for a specific team"""
        session = next(get_db())
        try:
            team = session.query(Team).filter_by(roster_id=roster_id).first()
            if not team:
                api.abort(404, f"Team with roster_id {roster_id} not found")
            
            # Get weekly results
            weekly_results = session.query(WeeklyResult).filter_by(
                roster_id=roster_id
            ).order_by(WeeklyResult.week).all()
            
            # Get matchup record
            wins = session.query(Matchup).filter(
                Matchup.winner_roster_id == roster_id
            ).count()
            
            total_matchups = session.query(Matchup).filter(
                (Matchup.team1_roster_id == roster_id) |
                (Matchup.team2_roster_id == roster_id)
            ).count()
            
            losses = total_matchups - wins
            
            # Calculate stats
            total_points = sum(r.total_bench_points for r in weekly_results)
            avg_points = total_points / len(weekly_results) if weekly_results else 0
            best_week = max((r.total_bench_points for r in weekly_results), default=0)
            worst_week = min((r.total_bench_points for r in weekly_results), default=0)
            
            return {
                'team': {
                    'roster_id': team.roster_id,
                    'team_name': team.team_name,
                    'owner_id': team.owner_id
                },
                'total_points': total_points,
                'average_points': round(avg_points, 2),
                'weeks_played': len(weekly_results),
                'best_week': best_week,
                'worst_week': worst_week,
                'wins': wins,
                'losses': losses,
                'win_percentage': round(wins / total_matchups, 3) if total_matchups > 0 else 0,
                'weekly_results': [{
                    'week': r.week,
                    'total_bench_points': r.total_bench_points,
                    'bench_player_count': r.bench_player_count,
                    'date_recorded': r.date_recorded.isoformat()
                } for r in weekly_results]
            }
            
        finally:
            session.close()
