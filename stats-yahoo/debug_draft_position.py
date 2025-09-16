#!/usr/bin/env python3
"""
Debug script to explore team object structure and find draft position data
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

def debug_team_structure():
    """Debug team object structure to find draft position."""
    try:
        print("🔍 Debugging team structure to find draft position...")
        ctx = Context()
        
        # Get a recent season with data
        year = 2024
        print(f"\nExploring {year} season...")
        
        leagues = ctx.get_leagues('nfl', year)
        target_league = None
        
        # Find Beer League
        for league in leagues:
            league_name = str(getattr(league, 'name', ''))
            if 'beer league' in league_name.lower():
                target_league = league
                print(f"Found league: {league_name}")
                break
        
        if not target_league:
            print("❌ Beer League not found")
            return
        
        # Get standings
        standings = target_league.standings()
        
        print(f"\n📊 Analyzing team objects (found {len(standings)} teams):")
        
        for i, team in enumerate(standings[:2], 1):  # Just analyze first 2 teams
            print(f"\n{'='*50}")
            print(f"TEAM {i}: {getattr(team, 'name', 'Unknown')}")
            print(f"{'='*50}")
            
            # Print all available attributes
            print("Available attributes:")
            for attr in dir(team):
                if not attr.startswith('_'):
                    try:
                        value = getattr(team, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except Exception as e:
                        print(f"  {attr}: <Error accessing: {e}>")
            
            # Check team_standings object
            if hasattr(team, 'team_standings'):
                print(f"\nteam_standings attributes:")
                for attr in dir(team.team_standings):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(team.team_standings, attr)
                            if not callable(value):
                                print(f"  team_standings.{attr}: {value}")
                        except Exception as e:
                            print(f"  team_standings.{attr}: <Error accessing: {e}>")
            
            # Check if there's draft-related data in the league
            print(f"\nChecking league-level draft data...")
            
        # Check league object for draft information
        print(f"\n{'='*50}")
        print("LEAGUE OBJECT ANALYSIS")
        print(f"{'='*50}")
        
        print("League attributes:")
        for attr in dir(target_league):
            if not attr.startswith('_') and 'draft' in attr.lower():
                try:
                    value = getattr(target_league, attr)
                    print(f"  {attr}: {value}")
                except Exception as e:
                    print(f"  {attr}: <Error accessing: {e}>")
        
        # Try to get draft results if available
        try:
            print(f"\nTrying to access draft results...")
            draft_results = target_league.draft_results()
            print(f"Draft results found! Type: {type(draft_results)}")
            
            if hasattr(draft_results, '__iter__'):
                for i, pick in enumerate(draft_results[:5]):  # Show first 5 picks
                    print(f"Pick {i+1}: {pick}")
                    
                    # Analyze pick object
                    for attr in dir(pick):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(pick, attr)
                                if not callable(value):
                                    print(f"    {attr}: {value}")
                            except Exception as e:
                                print(f"    {attr}: <Error: {e}>")
                    print()
                    
        except Exception as e:
            print(f"No draft results available: {e}")
            
        # Try alternative methods
        try:
            print(f"\nTrying alternative draft access methods...")
            
            # Check if teams have draft position directly
            for i, team in enumerate(standings[:3], 1):
                team_name = getattr(team, 'name', f'Team {i}')
                print(f"\nTeam: {team_name}")
                
                # Look for draft-related attributes
                for attr in dir(team):
                    if 'draft' in attr.lower() and not attr.startswith('_'):
                        try:
                            value = getattr(team, attr)
                            print(f"  {attr}: {value}")
                        except Exception as e:
                            print(f"  {attr}: <Error: {e}>")
                            
        except Exception as e:
            print(f"Error exploring alternative methods: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_team_structure()
