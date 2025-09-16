#!/usr/bin/env python3
"""
Debug script to check if 2018 Beer League data exists
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

def debug_2018():
    """Check if 2018 Beer League exists."""
    try:
        print("🔍 Checking for Beer League in 2018...")
        ctx = Context()
        
        # Check years around 2018
        for year in [2018, 2017, 2016, 2015]:
            print(f"\n{'='*30}")
            print(f"Checking year: {year}")
            print(f"{'='*30}")
            
            try:
                leagues = ctx.get_leagues('nfl', year)
                print(f"Found {len(leagues)} leagues for {year}")
                
                # Look for Beer League
                found_beer_league = False
                for i, league in enumerate(leagues, 1):
                    league_name = str(getattr(league, 'name', 'Unknown'))
                    league_key = str(getattr(league, 'league_key', 'Unknown'))
                    
                    print(f"  {i}. '{league_name}' ({league_key})")
                    
                    if 'beer league' in league_name.lower():
                        print(f"     ✅ FOUND BEER LEAGUE!")
                        found_beer_league = True
                
                if not found_beer_league:
                    print(f"  ❌ No Beer League found in {year}")
                    
            except Exception as e:
                print(f"❌ Error accessing {year}: {e}")
                
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    debug_2018()
