"""
JSON export functionality for dashboard integration.
Generates dashboard-ready JSON files directly from bench scoring data.
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from bench_scorer import WeeklyBenchResult, BenchMatchup, SeasonBenchStandings
from config import config

class JSONExporter:
    """Export bench scoring data to JSON format for static dashboard."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def get_file_path(self, filename: str) -> str:
        """Get full path for data file."""
        return os.path.join(self.data_dir, filename)
    
    def export_all_data(self, weekly_results: List[WeeklyBenchResult], matchups: List[BenchMatchup], standings: List[SeasonBenchStandings]) -> None:
        """Export all data to JSON files for dashboard."""
        print("📊 Exporting JSON data for dashboard...")
        
        # Extract teams data
        teams = self._extract_teams_data(weekly_results)
        
        # Generate all JSON files
        self.export_standings(standings)
        self.export_matchups(matchups, teams, weekly_results)
        self.export_analytics(weekly_results, matchups, standings)
        self.export_teams(teams)
        self.export_weekly_results(weekly_results)
        
        print("✅ JSON export complete!")
    
    def _extract_teams_data(self, weekly_results: List[WeeklyBenchResult]) -> Dict[int, Dict]:
        """Extract unique team data from weekly results."""
        teams = {}
        
        for result in weekly_results:
            if result.roster_id not in teams:
                teams[result.roster_id] = {
                    'roster_id': result.roster_id,
                    'team_name': result.team_name,
                    'owner_id': result.owner_id
                }
        
        return teams
    
    def export_standings(self, standings: List[SeasonBenchStandings]) -> None:
        """Export standings data to JSON."""
        standings_data = []
        
        for standing in standings:
            standings_data.append({
                'team': {
                    'roster_id': standing.roster_id,
                    'team_name': standing.team_name,
                    'owner_id': standing.owner_id
                },
                'total_points': round(standing.total_bench_points, 2),
                'average_points': round(standing.average_bench_points, 2),
                'weeks_played': standing.total_weeks,
                'best_week': round(standing.best_week_points, 2),
                'worst_week': round(standing.worst_week_points, 2),
                'wins': standing.wins,
                'losses': standing.losses,
                'win_percentage': round(standing.win_percentage, 3)
            })
        
        filepath = self.get_file_path('standings.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(standings_data, f, indent=2)
        
        print(f"📈 Exported standings data to {filepath}")
    
    def export_matchups(self, matchups: List[BenchMatchup], teams: Dict[int, Dict], weekly_results: List[WeeklyBenchResult] = None) -> None:
        """Export matchups data to JSON."""
        matchups_data = []
        
        for i, matchup in enumerate(matchups):
            team1 = teams.get(matchup.team1_roster_id, {})
            team2 = teams.get(matchup.team2_roster_id, {})
            winner = teams.get(matchup.winner_roster_id, {}) if matchup.winner_roster_id else None
            
            # Get bench players for both teams
            team1_bench_players = self._get_bench_players_for_matchup(matchup.team1_roster_id, matchup.week, weekly_results or [])
            team2_bench_players = self._get_bench_players_for_matchup(matchup.team2_roster_id, matchup.week, weekly_results or [])
            
            matchup_data = {
                'id': i + 1,
                'week': matchup.week,
                'matchup_id': matchup.matchup_id,
                'team1': {
                    'roster_id': matchup.team1_roster_id,
                    'team_name': matchup.team1_name,
                    'bench_points': round(matchup.team1_bench_points, 2),
                    'bench_players': team1_bench_players
                },
                'team2': {
                    'roster_id': matchup.team2_roster_id,
                    'team_name': matchup.team2_name,
                    'bench_points': round(matchup.team2_bench_points, 2),
                    'bench_players': team2_bench_players
                },
                'winner': {
                    'roster_id': matchup.winner_roster_id,
                    'team_name': matchup.team1_name if matchup.winner_roster_id == matchup.team1_roster_id else matchup.team2_name,
                    'bench_points': matchup.team1_bench_points if matchup.winner_roster_id == matchup.team1_roster_id else matchup.team2_bench_points,
                    'bench_players': team1_bench_players if matchup.winner_roster_id == matchup.team1_roster_id else team2_bench_players
                } if matchup.winner_roster_id else None,
                'margin_of_victory': round(matchup.margin_of_victory, 2) if matchup.margin_of_victory else None,
                'date_recorded': matchup.date_recorded.isoformat()
            }
            
            matchups_data.append(matchup_data)
        
        filepath = self.get_file_path('matchups.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(matchups_data, f, indent=2)
        
        print(f"🥊 Exported matchups data to {filepath}")
    
    def _get_bench_players_for_matchup(self, roster_id: int, week: int, weekly_results: List[WeeklyBenchResult]) -> List[Dict]:
        """Get bench players for a specific team and week from weekly results."""
        # Find the weekly result for this team and week
        for result in weekly_results:
            if result.roster_id == roster_id and result.week == week:
                bench_players = []
                for player in result.bench_players:
                    bench_players.append({
                        'player_id': player.player_id,
                        'name': player.player_name,
                        'position': player.position,
                        'team': player.team,
                        'points': round(player.points, 2)
                    })
                return bench_players
        return []
    
    def export_analytics(self, weekly_results: List[WeeklyBenchResult], matchups: List[BenchMatchup], standings: List[SeasonBenchStandings]) -> None:
        """Export analytics data to JSON."""
        weeks = sorted(set(r.week for r in weekly_results))
        total_teams = len(set(r.roster_id for r in weekly_results))
        
        # League stats
        all_points = [r.total_bench_points for r in weekly_results]
        league_stats = {
            'total_weeks': len(weeks),
            'total_teams': total_teams,
            'total_matchups': len(matchups),
            'average_weekly_points': round(sum(all_points) / len(all_points), 2) if all_points else 0,
            'highest_weekly_score': round(max(all_points), 2) if all_points else 0,
            'lowest_weekly_score': round(min(all_points), 2) if all_points else 0,
            'total_points_scored': round(sum(all_points), 2)
        }
        
        # Weekly trends
        weekly_trends = []
        for week in weeks:
            week_results = [r for r in weekly_results if r.week == week]
            week_points = [r.total_bench_points for r in week_results]
            
            if week_points:
                weekly_trends.append({
                    'week': week,
                    'average_points': round(sum(week_points) / len(week_points), 2),
                    'highest_score': round(max(week_points), 2),
                    'lowest_score': round(min(week_points), 2),
                    'total_points': round(sum(week_points), 2),
                    'teams_played': len(week_results)
                })
        
        # Team performance (convert standings to match expected format)
        team_performance = []
        for standing in standings:
            team_performance.append({
                'team': {
                    'roster_id': standing.roster_id,
                    'team_name': standing.team_name,
                    'owner_id': standing.owner_id
                },
                'total_points': round(standing.total_bench_points, 2),
                'average_points': round(standing.average_bench_points, 2),
                'weeks_played': standing.total_weeks,
                'best_week': round(standing.best_week_points, 2),
                'worst_week': round(standing.worst_week_points, 2),
                'wins': standing.wins,
                'losses': standing.losses,
                'win_percentage': round(standing.win_percentage, 3)
            })
        
        analytics_data = {
            'league_stats': league_stats,
            'weekly_trends': weekly_trends,
            'team_performance': team_performance
        }
        
        filepath = self.get_file_path('analytics.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, indent=2)
        
        print(f"📊 Exported analytics data to {filepath}")
    
    def export_teams(self, teams: Dict[int, Dict]) -> None:
        """Export teams data to JSON."""
        teams_array = list(teams.values())
        
        filepath = self.get_file_path('teams.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(teams_array, f, indent=2)
        
        print(f"👥 Exported teams data to {filepath}")
    
    def export_weekly_results(self, weekly_results: List[WeeklyBenchResult]) -> None:
        """Export weekly results data to JSON."""
        results_data = []
        
        for result in weekly_results:
            # Convert bench players to JSON-serializable format
            bench_players = []
            for player in result.bench_players:
                bench_players.append({
                    'player_id': player.player_id,
                    'name': player.player_name,
                    'position': player.position,
                    'team': player.team,
                    'points': round(player.points, 2)
                })
            
            results_data.append({
                'week': result.week,
                'roster_id': result.roster_id,
                'team_name': result.team_name,
                'total_bench_points': round(result.total_bench_points, 2),
                'bench_player_count': result.bench_player_count,
                'date_recorded': result.date_recorded.isoformat(),
                'bench_players_json': json.dumps(bench_players)
            })
        
        filepath = self.get_file_path('weekly-results.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"📅 Exported weekly results data to {filepath}")

# Convenience function
def export_dashboard_data(weekly_results: List[WeeklyBenchResult], matchups: List[BenchMatchup], standings: List[SeasonBenchStandings], data_dir: str = None) -> None:
    """Export all data for dashboard consumption."""
    if data_dir is None:
        data_dir = config.data_dir
    
    exporter = JSONExporter(data_dir)
    exporter.export_all_data(weekly_results, matchups, standings)
