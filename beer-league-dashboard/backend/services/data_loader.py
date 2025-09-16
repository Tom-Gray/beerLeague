import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import Team, WeeklyResult, Matchup
from database import get_db

class DataLoaderService:
    """Service for loading CSV data into the database."""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    def load_csv_files(self, session: Session) -> Dict[str, int]:
        """Load all CSV files from the data directory into the database."""
        results = {
            'teams': 0,
            'weekly_results': 0,
            'matchups': 0,
            'files_processed': 0
        }
        
        # Find the most recent CSV files
        weekly_results_files = list(self.data_dir.glob('weekly_results_*.csv'))
        matchups_files = list(self.data_dir.glob('weekly_matchups_*.csv'))
        
        if not weekly_results_files or not matchups_files:
            raise FileNotFoundError("No CSV files found in data directory")
        
        # Use the most recent files (sorted by filename which includes timestamp)
        latest_results_file = sorted(weekly_results_files)[-1]
        latest_matchups_file = sorted(matchups_files)[-1]
        
        print(f"Loading data from:")
        print(f"  - {latest_results_file.name}")
        print(f"  - {latest_matchups_file.name}")
        
        # Load teams first (extracted from weekly results)
        teams_loaded = self._load_teams_from_results(session, latest_results_file)
        results['teams'] = teams_loaded
        
        # Load weekly results
        weekly_results_loaded = self._load_weekly_results(session, latest_results_file)
        results['weekly_results'] = weekly_results_loaded
        
        # Load matchups
        matchups_loaded = self._load_matchups(session, latest_matchups_file)
        results['matchups'] = matchups_loaded
        
        results['files_processed'] = 2
        
        return results
    
    def _load_teams_from_results(self, session: Session, csv_file: Path) -> int:
        """Extract and load team data from weekly results CSV."""
        df = pd.read_csv(csv_file)
        
        # Get unique teams
        teams_data = df[['roster_id', 'owner_id', 'team_name']].drop_duplicates()
        
        teams_loaded = 0
        for _, row in teams_data.iterrows():
            # Check if team already exists
            existing_team = session.query(Team).filter_by(roster_id=row['roster_id']).first()
            
            if not existing_team:
                team = Team(
                    roster_id=row['roster_id'],
                    owner_id=row['owner_id'],
                    team_name=row['team_name']
                )
                session.add(team)
                teams_loaded += 1
        
        session.commit()
        return teams_loaded
    
    def _load_weekly_results(self, session: Session, csv_file: Path) -> int:
        """Load weekly results from CSV."""
        df = pd.read_csv(csv_file)
        
        # Clear existing weekly results
        session.query(WeeklyResult).delete()
        
        results_loaded = 0
        for _, row in df.iterrows():
            # Parse the date_recorded field
            date_recorded = pd.to_datetime(row['date_recorded'])
            
            weekly_result = WeeklyResult(
                week=row['week'],
                roster_id=row['roster_id'],
                total_bench_points=row['total_bench_points'],
                bench_player_count=row['bench_player_count'],
                date_recorded=date_recorded,
                bench_players_json=row.get('bench_players_detail', '[]')
            )
            session.add(weekly_result)
            results_loaded += 1
        
        session.commit()
        return results_loaded
    
    def _load_matchups(self, session: Session, csv_file: Path) -> int:
        """Load matchups from CSV."""
        df = pd.read_csv(csv_file)
        
        # Clear existing matchups
        session.query(Matchup).delete()
        
        matchups_loaded = 0
        for _, row in df.iterrows():
            # Parse the date_recorded field
            date_recorded = pd.to_datetime(row['date_recorded'])
            
            matchup = Matchup(
                week=row['week'],
                matchup_id=row['matchup_id'],
                team1_roster_id=row['team1_roster_id'],
                team1_bench_points=row['team1_bench_points'],
                team2_roster_id=row['team2_roster_id'],
                team2_bench_points=row['team2_bench_points'],
                winner_roster_id=row.get('winner_roster_id'),
                margin_of_victory=row.get('margin_of_victory'),
                date_recorded=date_recorded
            )
            session.add(matchup)
            matchups_loaded += 1
        
        session.commit()
        return matchups_loaded
    
    def get_available_files(self) -> Dict[str, List[str]]:
        """Get list of available CSV files in the data directory."""
        return {
            'weekly_results': [f.name for f in self.data_dir.glob('weekly_results_*.csv')],
            'matchups': [f.name for f in self.data_dir.glob('weekly_matchups_*.csv')],
            'standings': [f.name for f in self.data_dir.glob('season_standings_*.csv')]
        }
    
    def sync_database(self) -> Dict[str, int]:
        """Sync the database with the latest CSV files."""
        session = next(get_db())
        try:
            return self.load_csv_files(session)
        finally:
            session.close()

if __name__ == "__main__":
    # Test the data loader
    from config import Config
    
    config = Config()
    loader = DataLoaderService(config.DATA_DIR)
    
    print("Available files:")
    files = loader.get_available_files()
    for file_type, file_list in files.items():
        print(f"  {file_type}: {len(file_list)} files")
        for file_name in file_list[-3:]:  # Show last 3 files
            print(f"    - {file_name}")
    
    print("\nSyncing database...")
    results = loader.sync_database()
    print(f"Sync complete: {results}")
