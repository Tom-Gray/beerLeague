#!/usr/bin/env python3
"""
Debug script to see what leagues are available
"""

from yahoofantasy import Context

def debug_leagues():
    ctx = Context()
    
    print("Checking available leagues...")
    
    for year in [2024, 2023, 2022, 2021, 2020, 2019, 2018]:
        try:
            leagues = ctx.get_leagues('nfl', year)
            print(f"\n=== {year} NFL Leagues ===")
            print(f"Found {len(leagues)} leagues:")
            
            for i, league in enumerate(leagues):
                print(f"  League {i+1}:")
                print(f"    League ID: {getattr(league, 'league_id', 'N/A')}")
                print(f"    Name: {getattr(league, 'name', 'N/A')}")
                print(f"    League Key: {getattr(league, 'league_key', 'N/A')}")
                
                # Check if our target league ID is in this league's ID
                league_id_str = str(getattr(league, 'league_id', ''))
                if '848590' in league_id_str:
                    print(f"    *** FOUND TARGET LEAGUE! ***")
                
        except Exception as e:
            print(f"Error getting leagues for {year}: {e}")

if __name__ == '__main__':
    debug_leagues()
