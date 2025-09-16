#!/usr/bin/env python3
"""
Debug script to show all available leagues for 2023 and 2024
"""

import os
from dotenv import load_dotenv

try:
    from yahoofantasy import Context
except ImportError:
    print("Error: yahoofantasy package not installed. Run: pip install -r requirements.txt")
    exit(1)

# Load environment variables
load_dotenv()

def debug_leagues_for_years():
    """Debug leagues for 2023 and 2024."""
    try:
        print("🔍 Debugging leagues for 2023 and 2024...")
        ctx = Context()
        
        for year in [2024, 2023]:
            print(f"\n{'='*50}")
            print(f"YEAR: {year}")
            print(f"{'='*50}")
            
            try:
                leagues = ctx.get_leagues('nfl', year)
                print(f"Found {len(leagues)} leagues for {year}")
                
                for i, league in enumerate(leagues, 1):
                    league_id = getattr(league, 'league_id', 'N/A')
                    league_key = getattr(league, 'league_key', 'N/A')
                    league_name = getattr(league, 'name', 'N/A')
                    
                    print(f"\n{i}. League Name: '{league_name}'")
                    print(f"   League ID: {league_id}")
                    print(f"   League Key: {league_key}")
                    
                    # Check if this matches our target
                    target = "Beer League"
                    name_lower = str(league_name).lower()
                    target_lower = target.lower()
                    
                    if (target_lower in name_lower or 
                        name_lower in target_lower or
                        target_lower == name_lower):
                        print(f"   ✅ MATCHES TARGET: '{target}'")
                    else:
                        print(f"   ❌ Does not match: '{target}'")
                        
            except Exception as e:
                print(f"❌ Error getting leagues for {year}: {e}")
                
    except Exception as e:
        print(f"❌ Authentication or general error: {e}")

if __name__ == "__main__":
    debug_leagues_for_years()
