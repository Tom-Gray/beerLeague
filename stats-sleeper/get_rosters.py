
from sleeper_wrapper import League
import argparse
import json
from typing import Dict, List, Optional

def get_roster_owners(league_id: str) -> Dict[int, str]:
    """Map roster_id to owner info (display name or username)."""
    try:
        league = League(league_id)
        
        # Get users and rosters
        users = league.get_users()
        rosters = league.get_rosters()
        
        # Create mapping from user_id to display name
        user_names = {}
        for user in users:
            user_id = user.get('user_id')
            display_name = user.get('display_name') or user.get('username', f'User_{user_id}')
            user_names[user_id] = display_name
        
        # Create mapping from roster_id to owner name
        roster_owners = {}
        for roster in rosters:
            roster_id = roster.get('roster_id')
            owner_id = roster.get('owner_id')
            if roster_id and owner_id:
                roster_owners[roster_id] = user_names.get(owner_id, f'Owner_{owner_id}')
        
        return roster_owners
        
    except Exception as e:
        print(f"Error getting roster owners: {e}")
        return {}

def get_users_mapping(league_id: str) -> Dict[str, str]:
    """Map owner_id to display names."""
    try:
        league = League(league_id)
        users = league.get_users()
        
        user_mapping = {}
        for user in users:
            user_id = user.get('user_id')
            display_name = user.get('display_name') or user.get('username', f'User_{user_id}')
            user_mapping[user_id] = display_name
        
        return user_mapping
        
    except Exception as e:
        print(f"Error getting users mapping: {e}")
        return {}

def get_roster_with_slots(league_id: str, roster_id: int) -> Optional[Dict]:
    """Get roster data including player slot assignments."""
    try:
        league = League(league_id)
        rosters = league.get_rosters()
        
        for roster in rosters:
            if roster.get('roster_id') == roster_id:
                return roster
        
        return None
        
    except Exception as e:
        print(f"Error getting roster with slots for roster {roster_id}: {e}")
        return None

def identify_bench_players_from_roster(roster_data: Dict) -> List[str]:
    """Extract only bench (BN) slot players from roster data, excluding IR players."""
    if not roster_data:
        return []
    
    # Get all players and their slot assignments
    players = roster_data.get('players', [])
    starters = roster_data.get('starters', [])
    
    # In Sleeper, roster data includes:
    # - players: all players on roster
    # - starters: players in starting lineup (includes None for empty slots)
    # - The difference should be bench players, but we need to exclude IR
    
    # Convert to sets for efficient comparison
    all_players = set(players) if players else set()
    starting_players = set(player for player in starters if player is not None) if starters else set()
    
    # Players not in starting lineup (includes bench + IR)
    non_starters = all_players - starting_players
    
    # For now, return non-starters (we'll need to enhance this with actual slot data)
    # TODO: This still includes IR players - need to get actual slot assignments
    return list(non_starters)

def main():
    """Gets and prints the rosters for a Sleeper league."""
    parser = argparse.ArgumentParser(description="Get rosters for a Sleeper league.")
    parser.add_argument("league_id", help="The ID of the Sleeper league.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the JSON output.")
    args = parser.parse_args()

    try:
        league = League(args.league_id)
        rosters = league.get_rosters()
        print("Rosters:")
        if args.pretty:
            print(json.dumps(rosters, indent=4))
        else:
            print(rosters)
    except Exception as e:
        print(f"Error getting rosters: {e}")

if __name__ == "__main__":
    main()
