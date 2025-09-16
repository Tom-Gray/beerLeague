# Implementation Plan

## [Overview]
Build a comprehensive bench scoring system for the Beer League fantasy football competition that fetches weekly matchups from Sleeper API and tracks bench player performance.

This implementation will create a weekly bench scoring competition where teams compete based on the fantasy points scored by their bench players (players in BN roster slots). The system will traverse all weeks of the current season, fetch matchup data including individual player points, identify bench players by comparing roster players against starters, and maintain historical records of bench performance. This builds upon the existing sleeper-api-wrapper foundation and follows similar patterns to the Yahoo fantasy extraction system already in place.

## [Types]
Define data structures for bench player tracking, weekly scoring results, and competition standings.

```python
from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass
from datetime import datetime

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

class PlayerInfo(NamedTuple):
    player_id: str
    name: str
    position: str
    team: str
```

## [Files]
Create new modules for bench scoring functionality and update existing sleeper infrastructure.

**New files to be created:**
- `stats-sleeper/bench_scorer.py` - Core bench scoring logic and API integration
- `stats-sleeper/player_lookup.py` - Player ID to name/position mapping using Sleeper API
- `stats-sleeper/bench_data_manager.py` - Data persistence and CSV export functionality
- `stats-sleeper/bench_reporter.py` - Report generation and formatting
- `stats-sleeper/main_bench_scoring.py` - Main entry point for bench scoring system
- `stats-sleeper/config.py` - Configuration management for league settings
- `stats-sleeper/data/` - Directory for storing CSV exports and reports
- `stats-sleeper/requirements.txt` - Dependencies for sleeper-specific modules

**Existing files to be modified:**
- `stats-sleeper/get_matchups.py` - Add function to get matchups for specific week
- `stats-sleeper/get_rosters.py` - Add function to get user/team name mappings
- `stats-sleeper/README.md` - Update with bench scoring documentation

**Configuration files:**
- `stats-sleeper/.env.example` - Template for environment variables
- `stats-sleeper/.env` - League ID and configuration settings

## [Functions]
Implement core functions for data fetching, processing, and analysis.

**New functions in bench_scorer.py:**
- `get_league_info(league_id: str) -> Dict` - Fetch league metadata and settings
- `get_users_mapping(league_id: str) -> Dict[str, str]` - Map owner_id to display names
- `get_week_matchups(league_id: str, week: int) -> List[Dict]` - Fetch specific week matchups
- `identify_bench_players(roster_players: List[str], starters: List[str]) -> List[str]` - Find bench players
- `calculate_bench_points(bench_player_ids: List[str], players_points: Dict[str, float]) -> float` - Sum bench points
- `process_week_bench_scores(league_id: str, week: int) -> List[WeeklyBenchResult]` - Process entire week
- `create_weekly_matchups(weekly_results: List[WeeklyBenchResult], week: int) -> List[BenchMatchup]` - Create head-to-head matchups
- `determine_bench_winner(team1_points: float, team2_points: float) -> Tuple[int, float]` - Determine matchup winner and margin
- `get_season_weeks(league_id: str) -> List[int]` - Determine available weeks for season

**New functions in player_lookup.py:**
- `get_all_players() -> Dict[str, PlayerInfo]` - Fetch all NFL players from Sleeper API
- `lookup_player_info(player_id: str) -> Optional[PlayerInfo]` - Get player details by ID
- `cache_player_data(cache_file: str = "player_cache.json")` - Cache player data locally
- `load_cached_players(cache_file: str) -> Dict[str, PlayerInfo]` - Load cached player data

**New functions in bench_data_manager.py:**
- `save_weekly_results(results: List[WeeklyBenchResult], filename: str)` - Export weekly data to CSV
- `save_weekly_matchups(matchups: List[BenchMatchup], filename: str)` - Export matchup results to CSV
- `load_historical_data(filename: str) -> List[WeeklyBenchResult]` - Load previous results
- `load_matchup_history(filename: str) -> List[BenchMatchup]` - Load previous matchup results
- `calculate_season_standings(weekly_results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> List[SeasonBenchStandings]` - Generate standings with win/loss records
- `update_season_records(matchups: List[BenchMatchup]) -> List[SeasonRecord]` - Calculate win/loss records from matchups
- `export_season_summary(standings: List[SeasonBenchStandings], filename: str)` - Export season summary
- `export_matchup_summary(matchups: List[BenchMatchup], filename: str)` - Export all matchup results

**Modified functions in get_matchups.py:**
- `get_matchups_for_week(league_id: str, week: int) -> List[Dict]` - Extract existing logic into reusable function
- Update `main()` to use new function

**Modified functions in get_rosters.py:**
- `get_roster_owners(league_id: str) -> Dict[int, str]` - Map roster_id to owner info
- Update `main()` to use new function

## [Classes]
Create object-oriented components for managing bench scoring operations.

**New classes in bench_scorer.py:**
- `BenchScorer` - Main class for bench scoring operations
  - `__init__(self, league_id: str, cache_players: bool = True)`
  - `fetch_week_data(self, week: int) -> Tuple[List[WeeklyBenchResult], List[BenchMatchup]]`
  - `process_season(self, start_week: int = 1, end_week: Optional[int] = None) -> Tuple[List[WeeklyBenchResult], List[BenchMatchup]]`
  - `get_current_standings(self) -> List[SeasonBenchStandings]`
  - `create_matchups_from_results(self, weekly_results: List[WeeklyBenchResult], week: int) -> List[BenchMatchup]`

**New classes in bench_data_manager.py:**
- `BenchDataManager` - Handle data persistence and exports
  - `__init__(self, data_dir: str = "data")`
  - `save_results(self, results: List[WeeklyBenchResult], matchups: List[BenchMatchup], format: str = "csv")`
  - `load_results(self, filename: str) -> List[WeeklyBenchResult]`
  - `load_matchups(self, filename: str) -> List[BenchMatchup]`
  - `generate_reports(self, results: List[WeeklyBenchResult], matchups: List[BenchMatchup])`

**New classes in bench_reporter.py:**
- `BenchReporter` - Generate formatted reports and summaries
  - `__init__(self, data_manager: BenchDataManager)`
  - `create_weekly_report(self, week: int, results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> str`
  - `create_matchup_summary(self, week: int, matchups: List[BenchMatchup]) -> str`
  - `create_season_summary(self, standings: List[SeasonBenchStandings]) -> str`
  - `create_win_loss_table(self, standings: List[SeasonBenchStandings]) -> str`
  - `export_html_report(self, standings: List[SeasonBenchStandings], filename: str)`

## [Dependencies]
Add required packages for enhanced functionality and data management.

**New dependencies to add to stats-sleeper/requirements.txt:**
```
sleeper-api-wrapper>=1.0.4
pandas>=1.5.0
requests>=2.28.0
python-dotenv>=0.19.0
tabulate>=0.9.0
jinja2>=3.1.0
```

**Integration requirements:**
- Ensure compatibility with existing sleeper-api-wrapper version
- Add error handling for API rate limits and network issues
- Implement caching to reduce API calls for player data
- Add configuration management for league-specific settings

## [Testing]
Implement comprehensive testing strategy for API integration and data processing.

**Test file requirements:**
- `stats-sleeper/test_bench_scorer.py` - Unit tests for core scoring logic and matchup creation
- `stats-sleeper/test_player_lookup.py` - Tests for player data fetching and caching
- `stats-sleeper/test_data_manager.py` - Tests for data persistence and CSV operations
- `stats-sleeper/test_matchup_logic.py` - Tests for matchup pairing and winner determination
- `stats-sleeper/test_integration.py` - Integration tests with live API data

**Existing test modifications:**
- Update existing scripts to include error handling tests
- Add validation for API response formats
- Test edge cases like bye weeks, injured players, empty bench slots
- Test matchup creation with odd number of teams
- Test tie-breaking scenarios in bench scoring

**Validation strategies:**
- Compare calculated bench points against manual verification
- Validate player identification logic with known roster configurations  
- Test data export/import round-trip accuracy
- Verify season standings calculations with sample data
- Validate matchup pairing logic matches Sleeper's actual matchups
- Test win/loss record calculations and win percentage accuracy
- Verify margin of victory calculations

## [Implementation Order]
Execute implementation in logical sequence to minimize dependencies and ensure successful integration.

**Step 1:** Set up project structure and dependencies
- Create stats-sleeper/requirements.txt with all dependencies
- Create stats-sleeper/config.py for configuration management
- Create stats-sleeper/.env.example template
- Set up stats-sleeper/data/ directory for exports

**Step 2:** Implement player lookup functionality
- Create stats-sleeper/player_lookup.py with Sleeper API integration
- Implement player data caching to reduce API calls
- Add error handling for API failures and rate limits

**Step 3:** Enhance existing API integration
- Modify stats-sleeper/get_matchups.py to add week-specific function
- Modify stats-sleeper/get_rosters.py to add owner mapping function
- Test modifications with existing league ID

**Step 4:** Build core bench scoring logic
- Create stats-sleeper/bench_scorer.py with BenchScorer class
- Implement bench player identification and point calculation
- Add comprehensive error handling and logging

**Step 5:** Implement data management
- Create stats-sleeper/bench_data_manager.py for CSV operations
- Implement data persistence and historical tracking
- Add season standings calculation logic

**Step 6:** Create reporting system
- Create stats-sleeper/bench_reporter.py for formatted output
- Implement weekly and season summary reports
- Add HTML export functionality for enhanced presentation

**Step 7:** Build main application
- Create stats-sleeper/main_bench_scoring.py as primary entry point
- Implement command-line interface with argparse
- Add options for week ranges, output formats, and report types

**Step 8:** Testing and validation
- Create comprehensive test suite
- Validate against known data from Beer League
- Test edge cases and error conditions

**Step 9:** Documentation and deployment
- Update stats-sleeper/README.md with complete usage instructions
- Add example commands and output samples
- Create user guide for running bench scoring competition
