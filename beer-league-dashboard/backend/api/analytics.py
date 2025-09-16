from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import func, desc, asc
from models import Team, WeeklyResult, Matchup
from database import get_db
import json

api = Namespace('analytics', description='Advanced analytics and statistics')

# Response models
league_stats_model = api.model('LeagueStats', {
    'total_teams': fields.Integer(description='Total number of teams'),
    'total_weeks': fields.Integer(description='Total number of weeks played'),
    'total_matchups': fields.Integer(description='Total number of matchups'),
    'average_bench_points': fields.Float(description='League average bench points per week'),
    'highest_single_week': fields.Float(description='Highest single week bench score'),
    'lowest_single_week': fields.Float(description='Lowest single week bench score'),
    'total_bench_points': fields.Float(description='Total bench points scored league-wide')
})

trend_data_model = api.model('TrendData', {
    'week': fields.Integer(description='Week number'),
    'average_points': fields.Float(description='Average bench points for the week'),
    'highest_points': fields.Float(description='Highest bench points for the week'),
    'lowest_points': fields.Float(description='Lowest bench points for the week')
})

performance_distribution_model = api.model('PerformanceDistribution', {
    'range': fields.String(description='Point range (e.g., "0-10", "10-20")'),
    'count': fields.Integer(description='Number of performances in this range'),
    'percentage': fields.Float(description='Percentage of total performances')
})

@api.route('/league-stats')
class LeagueStats(Resource):
    @api.marshal_with(league_stats_model)
    def get(self):
        """Get overall league statistics"""
        session = next(get_db())
        try:
            # Basic counts
            total_teams = session.query(Team).count()
            total_weeks = session.query(func.max(WeeklyResult.week)).scalar() or 0
            total_matchups = session.query(Matchup).count()
            
            # Bench points statistics
            bench_stats = session.query(
                func.avg(WeeklyResult.total_bench_points).label('avg_points'),
                func.max(WeeklyResult.total_bench_points).label('max_points'),
                func.min(WeeklyResult.total_bench_points).label('min_points'),
                func.sum(WeeklyResult.total_bench_points).label('total_points')
            ).first()
            
            return {
                'total_teams': total_teams,
                'total_weeks': total_weeks,
                'total_matchups': total_matchups,
                'average_bench_points': round(float(bench_stats.avg_points or 0), 2),
                'highest_single_week': float(bench_stats.max_points or 0),
                'lowest_single_week': float(bench_stats.min_points or 0),
                'total_bench_points': float(bench_stats.total_points or 0)
            }
            
        finally:
            session.close()

@api.route('/weekly-trends')
class WeeklyTrends(Resource):
    @api.marshal_list_with(trend_data_model)
    def get(self):
        """Get weekly performance trends"""
        session = next(get_db())
        try:
            weekly_stats = session.query(
                WeeklyResult.week,
                func.avg(WeeklyResult.total_bench_points).label('avg_points'),
                func.max(WeeklyResult.total_bench_points).label('max_points'),
                func.min(WeeklyResult.total_bench_points).label('min_points')
            ).group_by(WeeklyResult.week).order_by(WeeklyResult.week).all()
            
            return [{
                'week': week,
                'average_points': round(float(avg_points), 2),
                'highest_points': float(max_points),
                'lowest_points': float(min_points)
            } for week, avg_points, max_points, min_points in weekly_stats]
            
        finally:
            session.close()

@api.route('/performance-distribution')
class PerformanceDistribution(Resource):
    @api.marshal_list_with(performance_distribution_model)
    def get(self):
        """Get distribution of bench performance ranges"""
        session = next(get_db())
        try:
            # Get all bench scores
            all_scores = session.query(WeeklyResult.total_bench_points).all()
            scores = [float(score[0]) for score in all_scores]
            
            if not scores:
                return []
            
            # Define ranges
            ranges = [
                (0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
                (50, 60), (60, 70), (70, 80), (80, 90), (90, 100),
                (100, float('inf'))
            ]
            
            total_count = len(scores)
            distribution = []
            
            for min_val, max_val in ranges:
                if max_val == float('inf'):
                    count = sum(1 for score in scores if score >= min_val)
                    range_label = f"{min_val}+"
                else:
                    count = sum(1 for score in scores if min_val <= score < max_val)
                    range_label = f"{min_val}-{max_val}"
                
                if count > 0:  # Only include ranges with data
                    percentage = (count / total_count) * 100
                    distribution.append({
                        'range': range_label,
                        'count': count,
                        'percentage': round(percentage, 1)
                    })
            
            return distribution
            
        finally:
            session.close()

@api.route('/team-consistency')
class TeamConsistency(Resource):
    def get(self):
        """Get team consistency metrics (standard deviation, coefficient of variation)"""
        session = next(get_db())
        try:
            teams = session.query(Team).all()
            consistency_data = []
            
            for team in teams:
                # Get all weekly scores for this team
                weekly_scores = session.query(WeeklyResult.total_bench_points).filter_by(
                    roster_id=team.roster_id
                ).all()
                
                if not weekly_scores:
                    continue
                
                scores = [float(score[0]) for score in weekly_scores]
                
                # Calculate statistics
                mean_score = sum(scores) / len(scores)
                variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
                std_dev = variance ** 0.5
                coefficient_of_variation = (std_dev / mean_score) * 100 if mean_score > 0 else 0
                
                consistency_data.append({
                    'team': {
                        'roster_id': team.roster_id,
                        'team_name': team.team_name
                    },
                    'games_played': len(scores),
                    'average_points': round(mean_score, 2),
                    'standard_deviation': round(std_dev, 2),
                    'coefficient_of_variation': round(coefficient_of_variation, 2),
                    'most_consistent': coefficient_of_variation < 20,  # Arbitrary threshold
                    'weekly_scores': scores
                })
            
            # Sort by coefficient of variation (most consistent first)
            consistency_data.sort(key=lambda x: x['coefficient_of_variation'])
            
            return consistency_data
            
        finally:
            session.close()

@api.route('/matchup-margins')
class MatchupMargins(Resource):
    def get(self):
        """Get analysis of matchup victory margins"""
        session = next(get_db())
        try:
            matchups = session.query(Matchup).filter(
                Matchup.margin_of_victory.isnot(None)
            ).all()
            
            if not matchups:
                return {
                    'total_matchups': 0,
                    'average_margin': 0,
                    'closest_matchups': [],
                    'biggest_blowouts': [],
                    'margin_distribution': []
                }
            
            margins = [float(m.margin_of_victory) for m in matchups]
            
            # Calculate statistics
            avg_margin = sum(margins) / len(margins)
            
            # Get closest matchups (smallest margins)
            closest_matchups = sorted(matchups, key=lambda x: x.margin_of_victory)[:5]
            
            # Get biggest blowouts (largest margins)
            biggest_blowouts = sorted(matchups, key=lambda x: x.margin_of_victory, reverse=True)[:5]
            
            # Margin distribution
            margin_ranges = [(0, 5), (5, 10), (10, 20), (20, 30), (30, float('inf'))]
            distribution = []
            
            for min_val, max_val in margin_ranges:
                if max_val == float('inf'):
                    count = sum(1 for margin in margins if margin >= min_val)
                    range_label = f"{min_val}+"
                else:
                    count = sum(1 for margin in margins if min_val <= margin < max_val)
                    range_label = f"{min_val}-{max_val}"
                
                percentage = (count / len(margins)) * 100
                distribution.append({
                    'range': range_label,
                    'count': count,
                    'percentage': round(percentage, 1)
                })
            
            # Format matchup details
            def format_matchup(matchup):
                team1 = session.query(Team).filter_by(roster_id=matchup.team1_roster_id).first()
                team2 = session.query(Team).filter_by(roster_id=matchup.team2_roster_id).first()
                winner = session.query(Team).filter_by(roster_id=matchup.winner_roster_id).first()
                
                return {
                    'week': matchup.week,
                    'team1_name': team1.team_name,
                    'team1_points': matchup.team1_bench_points,
                    'team2_name': team2.team_name,
                    'team2_points': matchup.team2_bench_points,
                    'winner_name': winner.team_name if winner else None,
                    'margin': matchup.margin_of_victory
                }
            
            return {
                'total_matchups': len(matchups),
                'average_margin': round(avg_margin, 2),
                'closest_matchups': [format_matchup(m) for m in closest_matchups],
                'biggest_blowouts': [format_matchup(m) for m in biggest_blowouts],
                'margin_distribution': distribution
            }
            
        finally:
            session.close()

@api.route('/power-rankings')
class PowerRankings(Resource):
    def get(self):
        """Get power rankings based on recent performance and strength of schedule"""
        weeks_to_consider = request.args.get('weeks', default=4, type=int)
        
        session = next(get_db())
        try:
            teams = session.query(Team).all()
            rankings = []
            
            for team in teams:
                # Get recent weekly results
                recent_results = session.query(WeeklyResult).filter_by(
                    roster_id=team.roster_id
                ).order_by(desc(WeeklyResult.week)).limit(weeks_to_consider).all()
                
                if not recent_results:
                    continue
                
                # Calculate recent average
                recent_scores = [r.total_bench_points for r in recent_results]
                recent_avg = sum(recent_scores) / len(recent_scores)
                
                # Get season average for comparison
                all_results = session.query(WeeklyResult).filter_by(
                    roster_id=team.roster_id
                ).all()
                season_avg = sum(r.total_bench_points for r in all_results) / len(all_results)
                
                # Calculate trend (recent vs season average)
                trend = recent_avg - season_avg
                
                # Get win percentage
                wins = session.query(Matchup).filter(
                    Matchup.winner_roster_id == team.roster_id
                ).count()
                total_matchups = session.query(Matchup).filter(
                    (Matchup.team1_roster_id == team.roster_id) |
                    (Matchup.team2_roster_id == team.roster_id)
                ).count()
                win_pct = wins / total_matchups if total_matchups > 0 else 0
                
                # Calculate power score (weighted combination of factors)
                power_score = (recent_avg * 0.4) + (season_avg * 0.3) + (win_pct * 100 * 0.2) + (trend * 0.1)
                
                rankings.append({
                    'team': {
                        'roster_id': team.roster_id,
                        'team_name': team.team_name
                    },
                    'power_score': round(power_score, 2),
                    'recent_average': round(recent_avg, 2),
                    'season_average': round(season_avg, 2),
                    'trend': round(trend, 2),
                    'win_percentage': round(win_pct, 3),
                    'recent_games': len(recent_results)
                })
            
            # Sort by power score
            rankings.sort(key=lambda x: x['power_score'], reverse=True)
            
            # Add ranking positions
            for i, ranking in enumerate(rankings):
                ranking['rank'] = i + 1
            
            return rankings
            
        finally:
            session.close()
