#!/usr/bin/env python3
"""
Yahoo Fantasy League Data Extractor

This module handles the extraction of historical data from Yahoo Fantasy leagues.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time

try:
    from yahoofantasy import Context, League
except ImportError:
    print("Error: yahoofantasy package not installed. Run: pip install -r requirements.txt")
    exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YahooFantasyExtractor:
    """Extract historical data from Yahoo Fantasy leagues."""
    
    def __init__(self, league_id: str):
        """Initialize the extractor with league ID."""
        self.league_id = league_id
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Yahoo API credentials not found. Run setup_auth.py first.")
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.league = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Yahoo Fantasy API."""
        try:
            self.logger.info("Authenticating with Yahoo Fantasy API...")
            
            # Use the yahoofantasy library's built-in authentication
            # This will use the stored credentials from 'yahoofantasy login'
            self.ctx = Context()
            
            # Test authentication by trying recent NFL seasons
            # NFL seasons are typically available from 2014 onwards
            current_year = datetime.now().year
            
            for test_year in [2023, 2022, 2021, 2020, 2019]:
                try:
                    leagues = self.ctx.get_leagues('nfl', test_year)
                    self.logger.info(f"Authentication successful! Found {len(leagues)} leagues for {test_year}")
                    return
                except Exception as e:
                    self.logger.debug(f"Could not get leagues for {test_year}: {e}")
                    continue
            
            # If we get here, authentication failed
            raise Exception("Could not authenticate - no valid NFL seasons found")
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise
    
    def get_available_seasons(self) -> List[str]:
        """Get all available seasons for the league."""
        try:
            self.logger.info("Fetching available seasons...")
            
            current_year = datetime.now().year
            seasons = []
            
            # Yahoo Fantasy NFL leagues go back to at least 2001
            # We'll search from 2024 back to 2001 (excluding current 2025 season)
            # but stop early if we hit consecutive failures
            start_year = 2024  # Don't include 2025 as it's not finished
            end_year = 2001
            consecutive_failures = 0
            max_consecutive_failures = 5  # Increased to handle API gaps for recent seasons
            
            self.logger.info(f"Searching for leagues from {start_year} back to {end_year}")
            self.logger.info("Note: Excluding 2025 season as it's not finished yet")
            
            for year in range(start_year, end_year - 1, -1):
                try:
                    # Get leagues for this year
                    leagues = self.ctx.get_leagues('nfl', year)
                    
                    # Check if our league ID exists in this year
                    found_league = False
                    for league in leagues:
                        league_id_str = str(getattr(league, 'league_id', ''))
                        league_key_str = str(getattr(league, 'league_key', ''))
                        league_name_str = str(getattr(league, 'name', ''))
                        
                        # Check if our target matches league_id, league_key, league_name, or is contained in any (case-insensitive)
                        target_lower = str(self.league_id).lower()
                        league_id_lower = league_id_str.lower()
                        league_key_lower = league_key_str.lower()
                        league_name_lower = league_name_str.lower()
                        
                        if (target_lower == league_key_lower or 
                            target_lower == league_id_lower or
                            target_lower == league_name_lower or
                            target_lower in league_key_lower or 
                            target_lower in league_id_lower or
                            target_lower in league_name_lower):
                            seasons.append(str(year))
                            self.logger.info(f"Found league for season {year}: '{league_name_str}' ({league_key_str})")
                            found_league = True
                            consecutive_failures = 0  # Reset failure counter
                            break
                    
                    if not found_league:
                        consecutive_failures += 1
                        self.logger.debug(f"No matching league found for {year} (consecutive failures: {consecutive_failures})")
                        
                        # If we've had too many consecutive failures and we already found some seasons,
                        # we can assume we've gone back far enough
                        if consecutive_failures >= max_consecutive_failures and len(seasons) > 0:
                            self.logger.info(f"Stopping search at {year} due to {consecutive_failures} consecutive failures")
                            break
                            
                except Exception as e:
                    consecutive_failures += 1
                    self.logger.debug(f"No league found for {year}: {e} (consecutive failures: {consecutive_failures})")
                    
                    # Same logic for API errors
                    if consecutive_failures >= max_consecutive_failures and len(seasons) > 0:
                        self.logger.info(f"Stopping search at {year} due to {consecutive_failures} consecutive API failures")
                        break
                    continue
            
            # Sort seasons in descending order (most recent first)
            seasons.sort(reverse=True)
            self.logger.info(f"Found available seasons: {seasons}")
            return seasons
            
        except Exception as e:
            self.logger.error(f"Error fetching seasons: {e}")
            return []
    
    def get_final_rankings(self, season: str) -> List[Dict]:
        """Get final rankings for a specific season."""
        try:
            self.logger.info(f"Fetching final rankings for {season} season...")
            
            # Get the league for this specific season
            leagues = self.ctx.get_leagues('nfl', int(season))
            target_league = None
            
            # Find our specific league
            for league in leagues:
                league_id_str = str(getattr(league, 'league_id', ''))
                league_key_str = str(getattr(league, 'league_key', ''))
                league_name_str = str(getattr(league, 'name', ''))
                
                # Check if our target matches league_id, league_key, league_name, or is contained in any (case-insensitive)
                target_lower = str(self.league_id).lower()
                league_id_lower = league_id_str.lower()
                league_key_lower = league_key_str.lower()
                league_name_lower = league_name_str.lower()
                
                if (target_lower == league_key_lower or 
                    target_lower == league_id_lower or
                    target_lower == league_name_lower or
                    target_lower in league_key_lower or 
                    target_lower in league_id_lower or
                    target_lower in league_name_lower):
                    target_league = league
                    break
            
            if not target_league:
                self.logger.warning(f"League {self.league_id} not found for season {season}")
                return []
            
            # Get standings for this league
            standings = target_league.standings()
            
            rankings = []
            for i, team in enumerate(standings, 1):
                # Use the correct API structure for team standings
                try:
                    outcomes = team.team_standings.outcome_totals
                    wins = int(outcomes.wins) if outcomes.wins is not None else 0
                    losses = int(outcomes.losses) if outcomes.losses is not None else 0
                    ties = int(outcomes.ties) if outcomes.ties is not None else 0
                    rank = int(team.team_standings.rank) if team.team_standings.rank is not None else i
                except (AttributeError, ValueError, TypeError):
                    # Fallback to basic attributes if the structure is different
                    wins = getattr(team, 'wins', 0)
                    losses = getattr(team, 'losses', 0)
                    ties = getattr(team, 'ties', 0)
                    rank = i
                
                # Get draft position if available
                draft_position = getattr(team, 'draft_position', None)
                
                ranking_data = {
                    'season': season,
                    'rank': rank,
                    'team_name': getattr(team, 'name', f'Team {i}'),
                    'team_key': getattr(team, 'team_key', ''),
                    'wins': wins,
                    'losses': losses,
                    'ties': ties,
                    'draft_position': int(draft_position) if draft_position is not None else None,
                    'points_for': getattr(team, 'points_for', 0),
                    'points_against': getattr(team, 'points_against', 0),
                    'extracted_date': datetime.now().isoformat()
                }
                rankings.append(ranking_data)
            
            self.logger.info(f"Extracted {len(rankings)} team rankings for {season}")
            return rankings
            
        except Exception as e:
            self.logger.error(f"Error fetching rankings for {season}: {e}")
            return []
    
    def get_highest_scores(self, season: str) -> List[Dict]:
        """Get highest weekly scores for a specific season."""
        try:
            self.logger.info(f"Fetching highest scores for {season} season...")
            
            # Get the league for this specific season
            leagues = self.ctx.get_leagues('nfl', int(season))
            target_league = None
            
            # Find our specific league
            for league in leagues:
                league_id_str = str(getattr(league, 'league_id', ''))
                league_key_str = str(getattr(league, 'league_key', ''))
                
                # Check if our target matches either the league_id, league_key, or is contained in either
                if (str(self.league_id) == league_key_str or 
                    str(self.league_id) == league_id_str or
                    str(self.league_id) in league_key_str or 
                    str(self.league_id) in league_id_str):
                    target_league = league
                    break
            
            if not target_league:
                self.logger.warning(f"League {self.league_id} not found for season {season}")
                return []
            
            highest_scores = []
            
            # Get available weeks for this league
            try:
                weeks = target_league.weeks()
                self.logger.info(f"Found {len(weeks)} weeks for season {season}")
            except Exception as e:
                self.logger.warning(f"Could not get weeks for {season}: {e}")
                # Fallback to standard NFL weeks
                weeks = list(range(1, 18))
            
            for week_num in (weeks if isinstance(weeks, list) else range(1, 18)):
                try:
                    week_number = week_num if isinstance(week_num, int) else getattr(week_num, 'week', week_num)
                    
                    # For now, we'll skip scoreboard extraction as it requires more complex API calls
                    # This is a placeholder for future implementation
                    self.logger.debug(f"Skipping scoreboard for week {week_number} - needs implementation")
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.warning(f"Could not process week {week_num} for {season}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(highest_scores)} highest weekly scores for {season}")
            return highest_scores
            
        except Exception as e:
            self.logger.error(f"Error fetching highest scores for {season}: {e}")
            return []
    
    def get_lowest_scores(self, season: str) -> List[Dict]:
        """Get lowest weekly scores for a specific season."""
        try:
            self.logger.info(f"Fetching lowest scores for {season} season...")
            
            # Get the league for this specific season
            leagues = self.ctx.get_leagues('nfl', int(season))
            target_league = None
            
            # Find our specific league
            for league in leagues:
                if str(self.league_id) in league.league_id:
                    target_league = league
                    break
            
            if not target_league:
                self.logger.warning(f"League {self.league_id} not found for season {season}")
                return []
            
            lowest_scores = []
            
            # Get available weeks for this league
            try:
                weeks = target_league.weeks()
                self.logger.info(f"Found {len(weeks)} weeks for season {season}")
            except Exception as e:
                self.logger.warning(f"Could not get weeks for {season}: {e}")
                # Fallback to standard NFL weeks
                weeks = list(range(1, 18))
            
            for week_num in (weeks if isinstance(weeks, list) else range(1, 18)):
                try:
                    week_number = week_num if isinstance(week_num, int) else getattr(week_num, 'week', week_num)
                    
                    # For now, we'll skip scoreboard extraction as it requires more complex API calls
                    # This is a placeholder for future implementation
                    self.logger.debug(f"Skipping scoreboard for week {week_number} - needs implementation")
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.warning(f"Could not process week {week_num} for {season}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(lowest_scores)} lowest weekly scores for {season}")
            return lowest_scores
            
        except Exception as e:
            self.logger.error(f"Error fetching lowest scores for {season}: {e}")
            return []
    
    def extract_all_data(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Extract all historical data for the league."""
        self.logger.info("Starting full data extraction...")
        
        seasons = self.get_available_seasons()
        
        all_rankings = []
        all_highest_scores = []
        all_lowest_scores = []
        
        for season in seasons:
            self.logger.info(f"Processing season {season}...")
            
            # Extract data for this season
            rankings = self.get_final_rankings(season)
            highest = self.get_highest_scores(season)
            lowest = self.get_lowest_scores(season)
            
            all_rankings.extend(rankings)
            all_highest_scores.extend(highest)
            all_lowest_scores.extend(lowest)
            
            # Rate limiting between seasons
            time.sleep(1)
        
        self.logger.info("Data extraction complete!")
        return all_rankings, all_highest_scores, all_lowest_scores
