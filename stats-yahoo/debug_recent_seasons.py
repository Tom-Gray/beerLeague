#!/usr/bin/env python3
"""
Debug script to find the most recent available NFL seasons
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

def debug_recent_seasons():
    """Find the most recent available NFL seasons."""
    try:
        print("🔍 Testing recent NFL seasons to find what's available...")
        ctx = Context()
        
        # Test years from 2025 back to 2020
        for year in range(2025, 2019, -1):
            print(f"\n{'='*30}")
            print(f"Testing year: {year}")
            print(f"{'='*30}")
            
            try:
                leagues = ctx.get_leagues('nfl', year)
                print(f"✅ SUCCESS: Found {len(leagues)} leagues for {year}")
                
                # Show first few leagues as examples
                for i, league in enumerate(leagues[:3], 1):
                    league_name = getattr(league, 'name', 'N/A')
                    league_key = getattr(league, 'league_key', 'N/A')
                    print(f"   {i}. '{league_name}' ({league_key})")
                
                if len(leagues) > 3:
                    print(f"   ... and {len(leagues) - 3} more leagues")
                    
            except Exception as e:
                print(f"❌ FAILED: {e}")
                
    except Exception as e:
        print(f"❌ Authentication or general error: {e}")

if __name__ == "__main__":
    debug_recent_seasons()
