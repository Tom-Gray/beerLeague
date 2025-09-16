
import requests
from sleeper_wrapper import League
import argparse
import json
from typing import List, Dict, Optional

def get_current_week():
    """Gets the current NFL week from the Sleeper API."""
    try:
        response = requests.get("https://api.sleeper.app/v1/state/nfl")
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["week"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting current week: {e}")
        return None

def get_matchups_for_week(league_id: str, week: int) -> List[Dict]:
    """Get matchups for a specific week."""
    try:
        league = League(league_id)
        matchups = league.get_matchups(week)
        return matchups if matchups else []
    except Exception as e:
        print(f"Error getting matchups for week {week}: {e}")
        return []

def get_league_info(league_id: str) -> Optional[Dict]:
    """Get league information."""
    try:
        league = League(league_id)
        return league.get_league()
    except Exception as e:
        print(f"Error getting league info: {e}")
        return None

def main():
    """Gets and prints the current matchups for a Sleeper league."""
    parser = argparse.ArgumentParser(description="Get current matchups for a Sleeper league.")
    parser.add_argument("league_id", help="The ID of the Sleeper league.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the JSON output.")
    args = parser.parse_args()

    current_week = get_current_week()

    if current_week:
        try:
            league = League(args.league_id)
            matchups = league.get_matchups(current_week)
            print(f"Matchups for week {current_week}:")
            if args.pretty:
                print(json.dumps(matchups, indent=4))
            else:
                print(matchups)
        except Exception as e:
            print(f"Error getting matchups: {e}")

if __name__ == "__main__":
    main()
