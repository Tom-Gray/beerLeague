"""
Configuration management for the bench scoring system.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for bench scoring system."""
    
    def __init__(self):
        self.league_id = os.getenv('SLEEPER_LEAGUE_ID', '1189882307887218688')
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.cache_players = os.getenv('CACHE_PLAYERS', 'true').lower() == 'true'
        self.player_cache_file = os.getenv('PLAYER_CACHE_FILE', 'player_cache.json')
        self.api_timeout = int(os.getenv('API_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
    @property
    def beer_league_id(self) -> str:
        """Get the Beer League ID."""
        return self.league_id
    
    def get_data_path(self, filename: str) -> str:
        """Get full path for data file."""
        return os.path.join(self.data_dir, filename)
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        if not self.league_id:
            raise ValueError("SLEEPER_LEAGUE_ID must be set")
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            
        return True

# Global config instance
config = Config()
