"""
Data persistence and CSV export functionality for bench scoring system.
"""
import csv
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from bench_scorer import WeeklyBenchResult, BenchMatchup, SeasonBenchStandings, SeasonRecord
from config import config

class BenchDataManager:
    """Handle data persistence and exports."""
    
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
    
    def save_weekly_results(self, results: List[WeeklyBenchResult], filename: str) -> None:
        """Export weekly data to CSV."""
        if not results:
            print("No weekly results to save")
            return
        
        filepath = self.get_file_path(filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'week', 'roster_id', 'owner_id', 'team_name', 
                    'total_bench_points', 'bench_player_count', 'date_recorded',
                    'bench_players_detail'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    # Create detailed bench players info
                    bench_detail = []
                    for player in result.bench_players:
                        bench_detail.append({
                            'player_id': player.player_id,
                            'name': player.player_name,
                            'position': player.position,
                            'team': player.team,
                            'points': player.points
                        })
                    
                    writer.writerow({
                        'week': result.week,
                        'roster_id': result.roster_id,
                        'owner_id': result.owner_id,
                        'team_name': result.team_name,
                        'total_bench_points': result.total_bench_points,
                        'bench_player_count': result.bench_player_count,
                        'date_recorded': result.date_recorded.isoformat(),
                        'bench_players_detail': json.dumps(bench_detail)
                    })
            
            print(f"Saved {len(results)} weekly results to {filepath}")
            
        except Exception as e:
            print(f"Error saving weekly results: {e}")
    
    def save_weekly_matchups(self, matchups: List[BenchMatchup], filename: str) -> None:
        """Export matchup results to CSV."""
        if not matchups:
            print("No matchups to save")
            return
        
        filepath = self.get_file_path(filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'week', 'matchup_id', 'team1_roster_id', 'team1_name', 'team1_bench_points',
                    'team2_roster_id', 'team2_name', 'team2_bench_points',
                    'winner_roster_id', 'margin_of_victory', 'date_recorded'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for matchup in matchups:
                    writer.writerow({
                        'week': matchup.week,
                        'matchup_id': matchup.matchup_id,
                        'team1_roster_id': matchup.team1_roster_id,
                        'team1_name': matchup.team1_name,
                        'team1_bench_points': matchup.team1_bench_points,
                        'team2_roster_id': matchup.team2_roster_id,
                        'team2_name': matchup.team2_name,
                        'team2_bench_points': matchup.team2_bench_points,
                        'winner_roster_id': matchup.winner_roster_id,
                        'margin_of_victory': matchup.margin_of_victory,
                        'date_recorded': matchup.date_recorded.isoformat()
                    })
            
            print(f"Saved {len(matchups)} matchups to {filepath}")
            
        except Exception as e:
            print(f"Error saving matchups: {e}")
    
    def load_historical_data(self, filename: str) -> List[WeeklyBenchResult]:
        """Load previous results."""
        filepath = self.get_file_path(filename)
        
        if not os.path.exists(filepath):
            print(f"No historical data found at {filepath}")
            return []
        
        try:
            results = []
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Parse bench players detail
                    bench_players = []
                    try:
                        bench_detail = json.loads(row['bench_players_detail'])
                        for player_data in bench_detail:
                            from bench_scorer import BenchPlayer
                            bench_player = BenchPlayer(
                                player_id=player_data['player_id'],
                                player_name=player_data['name'],
                                position=player_data['position'],
                                team=player_data['team'],
                                points=float(player_data['points']),
                                week=int(row['week']),
                                roster_id=int(row['roster_id']),
                                owner_id=row['owner_id']
                            )
                            bench_players.append(bench_player)
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Error parsing bench players for row: {e}")
                    
                    result = WeeklyBenchResult(
                        week=int(row['week']),
                        roster_id=int(row['roster_id']),
                        owner_id=row['owner_id'],
                        team_name=row['team_name'],
                        bench_players=bench_players,
                        total_bench_points=float(row['total_bench_points']),
                        bench_player_count=int(row['bench_player_count']),
                        date_recorded=datetime.fromisoformat(row['date_recorded'])
                    )
                    results.append(result)
            
            print(f"Loaded {len(results)} historical results from {filepath}")
            return results
            
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []
    
    def load_matchup_history(self, filename: str) -> List[BenchMatchup]:
        """Load previous matchup results."""
        filepath = self.get_file_path(filename)
        
        if not os.path.exists(filepath):
            print(f"No matchup history found at {filepath}")
            return []
        
        try:
            matchups = []
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    matchup = BenchMatchup(
                        week=int(row['week']),
                        matchup_id=int(row['matchup_id']),
                        team1_roster_id=int(row['team1_roster_id']),
                        team1_name=row['team1_name'],
                        team1_bench_points=float(row['team1_bench_points']),
                        team2_roster_id=int(row['team2_roster_id']),
                        team2_name=row['team2_name'],
                        team2_bench_points=float(row['team2_bench_points']),
                        winner_roster_id=int(row['winner_roster_id']),
                        margin_of_victory=float(row['margin_of_victory']),
                        date_recorded=datetime.fromisoformat(row['date_recorded'])
                    )
                    matchups.append(matchup)
            
            print(f"Loaded {len(matchups)} matchup history from {filepath}")
            return matchups
            
        except Exception as e:
            print(f"Error loading matchup history: {e}")
            return []
    
    def update_season_records(self, matchups: List[BenchMatchup]) -> List[SeasonRecord]:
        """Calculate win/loss records from matchups."""
        if not matchups:
            return []
        
        # Group matchups by team
        team_records = {}
        
        for matchup in matchups:
            # Process team 1
            if matchup.team1_roster_id not in team_records:
                team_records[matchup.team1_roster_id] = {
                    'roster_id': matchup.team1_roster_id,
                    'team_name': matchup.team1_name,
                    'wins': 0,
                    'losses': 0,
                    'total_points': 0.0,
                    'weeks': [],
                    'best_week': 0.0,
                    'best_week_num': 0,
                    'worst_week': float('inf'),
                    'worst_week_num': 0
                }
            
            # Process team 2
            if matchup.team2_roster_id not in team_records:
                team_records[matchup.team2_roster_id] = {
                    'roster_id': matchup.team2_roster_id,
                    'team_name': matchup.team2_name,
                    'wins': 0,
                    'losses': 0,
                    'total_points': 0.0,
                    'weeks': [],
                    'best_week': 0.0,
                    'best_week_num': 0,
                    'worst_week': float('inf'),
                    'worst_week_num': 0
                }
            
            # Update records
            team1_record = team_records[matchup.team1_roster_id]
            team2_record = team_records[matchup.team2_roster_id]
            
            # Add points and week data
            team1_record['total_points'] += matchup.team1_bench_points
            team1_record['weeks'].append(matchup.team1_bench_points)
            team2_record['total_points'] += matchup.team2_bench_points
            team2_record['weeks'].append(matchup.team2_bench_points)
            
            # Update best/worst weeks
            if matchup.team1_bench_points > team1_record['best_week']:
                team1_record['best_week'] = matchup.team1_bench_points
                team1_record['best_week_num'] = matchup.week
            if matchup.team1_bench_points < team1_record['worst_week']:
                team1_record['worst_week'] = matchup.team1_bench_points
                team1_record['worst_week_num'] = matchup.week
            
            if matchup.team2_bench_points > team2_record['best_week']:
                team2_record['best_week'] = matchup.team2_bench_points
                team2_record['best_week_num'] = matchup.week
            if matchup.team2_bench_points < team2_record['worst_week']:
                team2_record['worst_week'] = matchup.team2_bench_points
                team2_record['worst_week_num'] = matchup.week
            
            # Update win/loss records
            if matchup.winner_roster_id == matchup.team1_roster_id:
                team1_record['wins'] += 1
                team2_record['losses'] += 1
            else:
                team2_record['wins'] += 1
                team1_record['losses'] += 1
        
        # Convert to SeasonRecord objects
        season_records = []
        for roster_id, record in team_records.items():
            total_games = record['wins'] + record['losses']
            win_percentage = record['wins'] / total_games if total_games > 0 else 0.0
            avg_points = record['total_points'] / len(record['weeks']) if record['weeks'] else 0.0
            
            season_record = SeasonRecord(
                roster_id=roster_id,
                owner_id='',  # Will be filled in by caller if needed
                team_name=record['team_name'],
                wins=record['wins'],
                losses=record['losses'],
                win_percentage=round(win_percentage, 3),
                total_bench_points=round(record['total_points'], 2),
                average_bench_points=round(avg_points, 2),
                best_week_points=record['best_week'],
                best_week_number=record['best_week_num'],
                worst_week_points=record['worst_week'] if record['worst_week'] != float('inf') else 0.0,
                worst_week_number=record['worst_week_num']
            )
            season_records.append(season_record)
        
        return season_records
    
    def calculate_season_standings(self, weekly_results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> List[SeasonBenchStandings]:
        """Generate standings with win/loss records."""
        if not weekly_results and not matchups:
            return []
        
        # Get season records from matchups
        season_records = self.update_season_records(matchups)
        
        # Group weekly results by roster_id
        team_weekly_data = {}
        for result in weekly_results:
            if result.roster_id not in team_weekly_data:
                team_weekly_data[result.roster_id] = []
            team_weekly_data[result.roster_id].append(result)
        
        # Group matchups by roster_id
        team_matchups = {}
        for matchup in matchups:
            if matchup.team1_roster_id not in team_matchups:
                team_matchups[matchup.team1_roster_id] = []
            if matchup.team2_roster_id not in team_matchups:
                team_matchups[matchup.team2_roster_id] = []
            
            team_matchups[matchup.team1_roster_id].append(matchup)
            team_matchups[matchup.team2_roster_id].append(matchup)
        
        # Create standings
        standings = []
        
        for record in season_records:
            roster_id = record.roster_id
            weekly_data = team_weekly_data.get(roster_id, [])
            matchup_history = team_matchups.get(roster_id, [])
            
            # Get owner_id from weekly results if available
            owner_id = record.owner_id
            if weekly_data:
                owner_id = weekly_data[0].owner_id
            
            standing = SeasonBenchStandings(
                roster_id=roster_id,
                owner_id=owner_id,
                team_name=record.team_name,
                total_weeks=len(weekly_data),
                wins=record.wins,
                losses=record.losses,
                win_percentage=record.win_percentage,
                total_bench_points=record.total_bench_points,
                average_bench_points=record.average_bench_points,
                best_week_points=record.best_week_points,
                best_week_number=record.best_week_number,
                worst_week_points=record.worst_week_points,
                worst_week_number=record.worst_week_number,
                weekly_results=weekly_data,
                matchup_history=matchup_history
            )
            standings.append(standing)
        
        # Sort by win percentage, then by total points
        standings.sort(key=lambda x: (x.win_percentage, x.total_bench_points), reverse=True)
        
        return standings
    
    def export_season_summary(self, standings: List[SeasonBenchStandings], filename: str) -> None:
        """Export season summary."""
        if not standings:
            print("No standings to export")
            return
        
        filepath = self.get_file_path(filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'rank', 'roster_id', 'owner_id', 'team_name', 'total_weeks',
                    'wins', 'losses', 'win_percentage', 'total_bench_points',
                    'average_bench_points', 'best_week_points', 'best_week_number',
                    'worst_week_points', 'worst_week_number'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for rank, standing in enumerate(standings, 1):
                    writer.writerow({
                        'rank': rank,
                        'roster_id': standing.roster_id,
                        'owner_id': standing.owner_id,
                        'team_name': standing.team_name,
                        'total_weeks': standing.total_weeks,
                        'wins': standing.wins,
                        'losses': standing.losses,
                        'win_percentage': standing.win_percentage,
                        'total_bench_points': standing.total_bench_points,
                        'average_bench_points': standing.average_bench_points,
                        'best_week_points': standing.best_week_points,
                        'best_week_number': standing.best_week_number,
                        'worst_week_points': standing.worst_week_points,
                        'worst_week_number': standing.worst_week_number
                    })
            
            print(f"Exported season summary to {filepath}")
            
        except Exception as e:
            print(f"Error exporting season summary: {e}")
    
    def export_matchup_summary(self, matchups: List[BenchMatchup], filename: str) -> None:
        """Export all matchup results."""
        self.save_weekly_matchups(matchups, filename)
    
    def save_results(self, results: List[WeeklyBenchResult], matchups: List[BenchMatchup], format: str = "csv") -> None:
        """Save results in specified format."""
        if format.lower() == "csv":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if results:
                results_filename = f"weekly_results_{timestamp}.csv"
                self.save_weekly_results(results, results_filename)
            
            if matchups:
                matchups_filename = f"weekly_matchups_{timestamp}.csv"
                self.save_weekly_matchups(matchups, matchups_filename)
        else:
            print(f"Format {format} not supported yet")
    
    def load_results(self, filename: str) -> List[WeeklyBenchResult]:
        """Load results from file."""
        return self.load_historical_data(filename)
    
    def load_matchups(self, filename: str) -> List[BenchMatchup]:
        """Load matchups from file."""
        return self.load_matchup_history(filename)
    
    def generate_reports(self, results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> None:
        """Generate comprehensive reports."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate season standings
        standings = self.calculate_season_standings(results, matchups)
        
        if standings:
            standings_filename = f"season_standings_{timestamp}.csv"
            self.export_season_summary(standings, standings_filename)
        
        # Save raw data
        self.save_results(results, matchups)
        
        print(f"Generated reports with timestamp {timestamp}")

# Convenience functions
def save_weekly_results(results: List[WeeklyBenchResult], filename: str) -> None:
    """Export weekly data to CSV."""
    manager = BenchDataManager(config.data_dir)
    manager.save_weekly_results(results, filename)

def save_weekly_matchups(matchups: List[BenchMatchup], filename: str) -> None:
    """Export matchup results to CSV."""
    manager = BenchDataManager(config.data_dir)
    manager.save_weekly_matchups(matchups, filename)

def load_historical_data(filename: str) -> List[WeeklyBenchResult]:
    """Load previous results."""
    manager = BenchDataManager(config.data_dir)
    return manager.load_historical_data(filename)

def load_matchup_history(filename: str) -> List[BenchMatchup]:
    """Load previous matchup results."""
    manager = BenchDataManager(config.data_dir)
    return manager.load_matchup_history(filename)

def calculate_season_standings(weekly_results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> List[SeasonBenchStandings]:
    """Generate standings with win/loss records."""
    manager = BenchDataManager(config.data_dir)
    return manager.calculate_season_standings(weekly_results, matchups)

def update_season_records(matchups: List[BenchMatchup]) -> List[SeasonRecord]:
    """Calculate win/loss records from matchups."""
    manager = BenchDataManager(config.data_dir)
    return manager.update_season_records(matchups)

def export_season_summary(standings: List[SeasonBenchStandings], filename: str) -> None:
    """Export season summary."""
    manager = BenchDataManager(config.data_dir)
    manager.export_season_summary(standings, filename)

def export_matchup_summary(matchups: List[BenchMatchup], filename: str) -> None:
    """Export all matchup results."""
    manager = BenchDataManager(config.data_dir)
    manager.export_matchup_summary(matchups, filename)
