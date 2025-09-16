"""
Player lookup functionality for the bench scoring system.
Handles fetching and caching player data from Sleeper API.
"""
import json
import os
import time
from typing import Dict, Optional, NamedTuple
import requests
from config import config

class PlayerInfo(NamedTuple):
    player_id: str
    name: str
    position: str
    team: str

class PlayerLookup:
    """Handles player data fetching and caching."""
    
    def __init__(self, cache_file: Optional[str] = None):
        self.cache_file = cache_file or config.get_data_path(config.player_cache_file)
        self.players_cache: Dict[str, PlayerInfo] = {}
        self.cache_loaded = False
    
    def get_all_players(self) -> Dict[str, PlayerInfo]:
        """Fetch all NFL players from Sleeper API."""
        if self.cache_loaded and self.players_cache:
            return self.players_cache
        
        # Try to load from cache first
        if os.path.exists(self.cache_file):
            try:
                cached_players = self.load_cached_players()
                if cached_players:
                    self.players_cache = cached_players
                    self.cache_loaded = True
                    print(f"Loaded {len(cached_players)} players from cache")
                    return cached_players
            except Exception as e:
                print(f"Error loading cached players: {e}")
        
        # Fetch from API if cache doesn't exist or failed to load
        print("Fetching player data from Sleeper API...")
        try:
            response = requests.get(
                "https://api.sleeper.app/v1/players/nfl",
                timeout=config.api_timeout
            )
            response.raise_for_status()
            
            raw_players = response.json()
            players_dict = {}
            
            for player_id, player_data in raw_players.items():
                if player_data and isinstance(player_data, dict):
                    # Extract player information
                    name = f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip()
                    if not name:
                        name = player_data.get('full_name', f"Player_{player_id}")
                    
                    position = player_data.get('position', 'UNK')
                    team = player_data.get('team', 'FA')
                    
                    # Only include players with valid data
                    if name and name != f"Player_{player_id}":
                        players_dict[player_id] = PlayerInfo(
                            player_id=player_id,
                            name=name,
                            position=position,
                            team=team or 'FA'
                        )
            
            self.players_cache = players_dict
            self.cache_loaded = True
            
            # Cache the data
            if config.cache_players:
                self.cache_player_data(players_dict)
            
            print(f"Fetched {len(players_dict)} players from Sleeper API")
            return players_dict
            
        except requests.RequestException as e:
            print(f"Error fetching players from API: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error fetching players: {e}")
            return {}
    
    def lookup_player_info(self, player_id: str) -> Optional[PlayerInfo]:
        """Get player details by ID."""
        if not self.cache_loaded:
            self.get_all_players()
        
        return self.players_cache.get(player_id)
    
    def cache_player_data(self, players_dict: Dict[str, PlayerInfo]) -> None:
        """Cache player data locally."""
        try:
            # Convert PlayerInfo objects to dictionaries for JSON serialization
            cache_data = {
                'timestamp': time.time(),
                'players': {
                    player_id: {
                        'player_id': info.player_id,
                        'name': info.name,
                        'position': info.position,
                        'team': info.team
                    }
                    for player_id, info in players_dict.items()
                }
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"Cached {len(players_dict)} players to {self.cache_file}")
            
        except Exception as e:
            print(f"Error caching player data: {e}")
    
    def load_cached_players(self) -> Dict[str, PlayerInfo]:
        """Load cached player data."""
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is recent (less than 24 hours old)
            cache_age = time.time() - cache_data.get('timestamp', 0)
            if cache_age > 86400:  # 24 hours in seconds
                print("Player cache is older than 24 hours, will refresh from API")
                return {}
            
            # Convert dictionary data back to PlayerInfo objects
            players_dict = {}
            for player_id, player_data in cache_data.get('players', {}).items():
                players_dict[player_id] = PlayerInfo(
                    player_id=player_data['player_id'],
                    name=player_data['name'],
                    position=player_data['position'],
                    team=player_data['team']
                )
            
            return players_dict
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading cached players: {e}")
            return {}
    
    def refresh_cache(self) -> Dict[str, PlayerInfo]:
        """Force refresh of player cache."""
        self.cache_loaded = False
        self.players_cache = {}
        
        # Remove existing cache file
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        
        return self.get_all_players()

# Global player lookup instance
player_lookup = PlayerLookup()

# Convenience functions
def get_all_players() -> Dict[str, PlayerInfo]:
    """Get all NFL players."""
    return player_lookup.get_all_players()

def lookup_player_info(player_id: str) -> Optional[PlayerInfo]:
    """Get player details by ID."""
    return player_lookup.lookup_player_info(player_id)

def cache_player_data(cache_file: str = "player_cache.json") -> None:
    """Cache player data locally."""
    players = get_all_players()
    if players:
        player_lookup.cache_player_data(players)

def load_cached_players(cache_file: str = "player_cache.json") -> Dict[str, PlayerInfo]:
    """Load cached player data."""
    lookup = PlayerLookup(cache_file)
    return lookup.load_cached_players()
