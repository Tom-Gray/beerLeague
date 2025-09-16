"""
Core bench scoring logic and API integration.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
from sleeper_wrapper import League
from get_matchups import get_matchups_for_week, get_league_info, get_current_week
from get_rosters import get_roster_owners, get_users_mapping
from player_lookup import lookup_player_info, PlayerInfo
from config import config

@dataclass
class BenchPlayer:
    player_id: str
    player_name: str
    position: str
    team: str
    points: float
    week: int
    roster_id: int
    owner_id: str

@dataclass
class WeeklyBenchResult:
    week: int
    roster_id: int
    owner_id: str
    team_name: str
    bench_players: List[BenchPlayer]
    total_bench_points: float
    bench_player_count: int
    date_recorded: datetime

@dataclass
class BenchMatchup:
    week: int
    matchup_id: int
    team1_roster_id: int
    team1_name: str
    team1_bench_points: float
    team2_roster_id: int
    team2_name: str
    team2_bench_points: float
    winner_roster_id: int
    margin_of_victory: float
    date_recorded: datetime

@dataclass
class SeasonRecord:
    roster_id: int
    owner_id: str
    team_name: str
    wins: int
    losses: int
    win_percentage: float
    total_bench_points: float
    average_bench_points: float
    best_week_points: float
    best_week_number: int
    worst_week_points: float
    worst_week_number: int

@dataclass
class SeasonBenchStandings:
    roster_id: int
    owner_id: str
    team_name: str
    total_weeks: int
    wins: int
    losses: int
    win_percentage: float
    total_bench_points: float
    average_bench_points: float
    best_week_points: float
    best_week_number: int
    worst_week_points: float
    worst_week_number: int
    weekly_results: List[WeeklyBenchResult]
    matchup_history: List[BenchMatchup]

class BenchScorer:
    """Main class for bench scoring operations."""
    
    def __init__(self, league_id: str, cache_players: bool = True):
        self.league_id = league_id
        self.cache_players = cache_players
        self.league = League(league_id)
        self.roster_owners = {}
        self.users_mapping = {}
        self._load_league_data()
    
    def _load_league_data(self):
        """Load league data including roster owners and users."""
        try:
            self.roster_owners = get_roster_owners(self.league_id)
            self.users_mapping = get_users_mapping(self.league_id)
            print(f"Loaded data for {len(self.roster_owners)} teams")
        except Exception as e:
            print(f"Error loading league data: {e}")
    
    def get_league_info(self) -> Optional[Dict]:
        """Fetch league metadata and settings."""
        return get_league_info(self.league_id)
    
    def get_season_weeks(self) -> List[int]:
        """Determine available weeks for season."""
        try:
            league_info = self.get_league_info()
            if not league_info:
                return []
            
            # Get current week to determine how many weeks have been played
            current_week = get_current_week()
            if not current_week:
                return []
            
            # Return weeks 1 through current week
            return list(range(1, current_week + 1))
            
        except Exception as e:
            print(f"Error getting season weeks: {e}")
            return []
    
    def identify_bench_players(self, roster_players: List[str], starters: List[str], reserve_players: List[str] = None) -> List[str]:
        """Find bench players by comparing roster players against starters and excluding IR (reserve) players."""
        if not roster_players or not starters:
            return []
        
        # Convert to sets for efficient comparison
        roster_set = set(roster_players)
        starters_set = set(starters)
        reserve_set = set(reserve_players) if reserve_players else set()
        
        # Bench players are those in roster but not in starters and not in IR (reserve)
        bench_players = list(roster_set - starters_set - reserve_set)
        return bench_players
    
    def calculate_bench_points(self, bench_player_ids: List[str], players_points: Dict[str, float]) -> float:
        """Sum bench points from players_points dict."""
        total_points = 0.0
        
        for player_id in bench_player_ids:
            if player_id in players_points:
                points = players_points.get(player_id, 0.0)
                if isinstance(points, (int, float)):
                    total_points += float(points)
        
        return round(total_points, 2)
    
    def process_week_bench_scores(self, week: int) -> List[WeeklyBenchResult]:
        """Process entire week and return bench results for all teams."""
        try:
            matchups = get_matchups_for_week(self.league_id, week)
            if not matchups:
                print(f"No matchups found for week {week}")
                return []
            
            # Get roster data to access reserve (IR) players
            rosters = self.league.get_rosters()
            roster_reserve_map = {}
            for roster in rosters:
                roster_id = roster.get('roster_id')
                reserve_players = roster.get('reserve', [])
                if roster_id:
                    roster_reserve_map[roster_id] = reserve_players
            
            weekly_results = []
            
            for matchup in matchups:
                roster_id = matchup.get('roster_id')
                if not roster_id:
                    continue
                
                # Get roster data
                players = matchup.get('players', [])
                starters = matchup.get('starters', [])
                players_points = matchup.get('players_points', {})
                
                # Get reserve (IR) players for this roster
                reserve_players = roster_reserve_map.get(roster_id, [])
                
                # Identify bench players (excluding IR players)
                bench_player_ids = self.identify_bench_players(players, starters, reserve_players)
                
                # Calculate bench points
                total_bench_points = self.calculate_bench_points(bench_player_ids, players_points)
                
                # Get team/owner info
                team_name = self.roster_owners.get(roster_id, f'Team_{roster_id}')
                
                # Find owner_id from roster data
                owner_id = None
                try:
                    rosters = self.league.get_rosters()
                    for roster in rosters:
                        if roster.get('roster_id') == roster_id:
                            owner_id = roster.get('owner_id')
                            break
                except Exception as e:
                    print(f"Error getting owner_id for roster {roster_id}: {e}")
                
                if not owner_id:
                    owner_id = f'owner_{roster_id}'
                
                # Create bench player objects with detailed info
                bench_players = []
                for player_id in bench_player_ids:
                    player_info = lookup_player_info(player_id)
                    points = players_points.get(player_id, 0.0)
                    
                    if player_info:
                        bench_player = BenchPlayer(
                            player_id=player_id,
                            player_name=player_info.name,
                            position=player_info.position,
                            team=player_info.team,
                            points=float(points) if isinstance(points, (int, float)) else 0.0,
                            week=week,
                            roster_id=roster_id,
                            owner_id=owner_id
                        )
                    else:
                        bench_player = BenchPlayer(
                            player_id=player_id,
                            player_name=f'Player_{player_id}',
                            position='UNK',
                            team='UNK',
                            points=float(points) if isinstance(points, (int, float)) else 0.0,
                            week=week,
                            roster_id=roster_id,
                            owner_id=owner_id
                        )
                    
                    bench_players.append(bench_player)
                
                # Create weekly result
                weekly_result = WeeklyBenchResult(
                    week=week,
                    roster_id=roster_id,
                    owner_id=owner_id,
                    team_name=team_name,
                    bench_players=bench_players,
                    total_bench_points=total_bench_points,
                    bench_player_count=len(bench_players),
                    date_recorded=datetime.now()
                )
                
                weekly_results.append(weekly_result)
            
            print(f"Processed week {week}: {len(weekly_results)} teams")
            return weekly_results
            
        except Exception as e:
            print(f"Error processing week {week}: {e}")
            return []
    
    def create_weekly_matchups(self, weekly_results: List[WeeklyBenchResult], week: int) -> List[BenchMatchup]:
        """Create head-to-head matchups from weekly results."""
        try:
            # Get actual Sleeper matchups to determine pairings
            sleeper_matchups = get_matchups_for_week(self.league_id, week)
            if not sleeper_matchups:
                return []
            
            # Group teams by matchup_id
            matchup_groups = {}
            for matchup in sleeper_matchups:
                matchup_id = matchup.get('matchup_id')
                roster_id = matchup.get('roster_id')
                
                if matchup_id and roster_id:
                    if matchup_id not in matchup_groups:
                        matchup_groups[matchup_id] = []
                    matchup_groups[matchup_id].append(roster_id)
            
            # Create bench matchups
            bench_matchups = []
            
            for matchup_id, roster_ids in matchup_groups.items():
                if len(roster_ids) == 2:  # Standard head-to-head matchup
                    roster1_id, roster2_id = roster_ids
                    
                    # Find bench results for these teams
                    team1_result = None
                    team2_result = None
                    
                    for result in weekly_results:
                        if result.roster_id == roster1_id:
                            team1_result = result
                        elif result.roster_id == roster2_id:
                            team2_result = result
                    
                    if team1_result and team2_result:
                        # Determine winner
                        if team1_result.total_bench_points > team2_result.total_bench_points:
                            winner_roster_id = roster1_id
                            margin = team1_result.total_bench_points - team2_result.total_bench_points
                        elif team2_result.total_bench_points > team1_result.total_bench_points:
                            winner_roster_id = roster2_id
                            margin = team2_result.total_bench_points - team1_result.total_bench_points
                        else:
                            winner_roster_id = roster1_id  # Tie goes to first team
                            margin = 0.0
                        
                        bench_matchup = BenchMatchup(
                            week=week,
                            matchup_id=matchup_id,
                            team1_roster_id=roster1_id,
                            team1_name=team1_result.team_name,
                            team1_bench_points=team1_result.total_bench_points,
                            team2_roster_id=roster2_id,
                            team2_name=team2_result.team_name,
                            team2_bench_points=team2_result.total_bench_points,
                            winner_roster_id=winner_roster_id,
                            margin_of_victory=round(margin, 2),
                            date_recorded=datetime.now()
                        )
                        
                        bench_matchups.append(bench_matchup)
            
            print(f"Created {len(bench_matchups)} bench matchups for week {week}")
            return bench_matchups
            
        except Exception as e:
            print(f"Error creating weekly matchups for week {week}: {e}")
            return []
    
    def determine_bench_winner(self, team1_points: float, team2_points: float) -> Tuple[int, float]:
        """Determine matchup winner and margin (returns winner_index, margin)."""
        if team1_points > team2_points:
            return 0, team1_points - team2_points  # Team 1 wins
        elif team2_points > team1_points:
            return 1, team2_points - team1_points  # Team 2 wins
        else:
            return 0, 0.0  # Tie goes to team 1
    
    def fetch_week_data(self, week: int) -> Tuple[List[WeeklyBenchResult], List[BenchMatchup]]:
        """Fetch and process data for a specific week."""
        print(f"Processing week {week}...")
        
        # Get weekly bench results
        weekly_results = self.process_week_bench_scores(week)
        
        # Create matchups from results
        matchups = self.create_weekly_matchups(weekly_results, week)
        
        return weekly_results, matchups
    
    def process_season(self, start_week: int = 1, end_week: Optional[int] = None) -> Tuple[List[WeeklyBenchResult], List[BenchMatchup]]:
        """Process multiple weeks of the season."""
        if end_week is None:
            available_weeks = self.get_season_weeks()
            end_week = max(available_weeks) if available_weeks else start_week
        
        all_results = []
        all_matchups = []
        
        for week in range(start_week, end_week + 1):
            try:
                weekly_results, matchups = self.fetch_week_data(week)
                all_results.extend(weekly_results)
                all_matchups.extend(matchups)
                
                # Small delay to be respectful to API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing week {week}: {e}")
                continue
        
        print(f"Season processing complete: {len(all_results)} team results, {len(all_matchups)} matchups")
        return all_results, all_matchups
    
    def create_matchups_from_results(self, weekly_results: List[WeeklyBenchResult], week: int) -> List[BenchMatchup]:
        """Create matchups from weekly results (alias for create_weekly_matchups)."""
        return self.create_weekly_matchups(weekly_results, week)
