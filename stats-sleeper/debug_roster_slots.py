#!/usr/bin/env python3
"""
Debug script to understand Sleeper roster slot structure and IR player identification.
"""

import requests
import json
from sleeper_wrapper import League
from config import config

def debug_roster_structure():
    """Debug the structure of roster data from Sleeper API."""
    league_id = config.league_id
    
    print(f"Debugging roster structure for league: {league_id}")
    print("=" * 60)
    
    try:
        # Method 1: Using sleeper_wrapper
        print("\n1. Using sleeper_wrapper League.get_rosters():")
        league = League(league_id)
        rosters = league.get_rosters()
        
        if rosters and len(rosters) > 0:
            print(f"Found {len(rosters)} rosters")
            print("\nSample roster structure:")
            print(json.dumps(rosters[0], indent=2))
        else:
            print("No rosters found or error occurred")
            
    except Exception as e:
        print(f"Error with sleeper_wrapper: {e}")
    
    try:
        # Method 2: Direct API call to rosters endpoint
        print(f"\n2. Direct API call to rosters endpoint:")
        url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        response = requests.get(url)
        
        if response.status_code == 200:
            rosters_data = response.json()
            print(f"Found {len(rosters_data)} rosters via direct API")
            if rosters_data:
                print("\nSample roster structure (direct API):")
                print(json.dumps(rosters_data[0], indent=2))
        else:
            print(f"API call failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"Error with direct API call: {e}")
    
    try:
        # Method 3: Check matchup data structure for roster info
        print(f"\n3. Checking matchup data for roster slot info:")
        current_week = get_current_week()
        if current_week:
            matchup_url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{current_week}"
            response = requests.get(matchup_url)
            
            if response.status_code == 200:
                matchups = response.json()
                print(f"Found {len(matchups)} matchups for week {current_week}")
                if matchups:
                    print("\nSample matchup structure:")
                    print(json.dumps(matchups[0], indent=2))
            else:
                print(f"Matchup API call failed with status: {response.status_code}")
                
    except Exception as e:
        print(f"Error checking matchup data: {e}")

def get_current_week():
    """Get current NFL week."""
    try:
        response = requests.get("https://api.sleeper.app/v1/state/nfl")
        if response.status_code == 200:
            return response.json().get("week")
    except:
        pass
    return None

def debug_league_settings():
    """Check league settings for roster configuration."""
    league_id = config.league_id
    
    try:
        print(f"\n4. League settings and roster configuration:")
        url = f"https://api.sleeper.app/v1/league/{league_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            league_data = response.json()
            roster_positions = league_data.get('roster_positions', [])
            settings = league_data.get('settings', {})
            
            print(f"Roster positions: {roster_positions}")
            print(f"Relevant settings:")
            for key, value in settings.items():
                if 'roster' in key.lower() or 'ir' in key.lower() or 'bench' in key.lower():
                    print(f"  {key}: {value}")
                    
    except Exception as e:
        print(f"Error getting league settings: {e}")

if __name__ == "__main__":
    debug_roster_structure()
    debug_league_settings()
