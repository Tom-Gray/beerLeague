#!/usr/bin/env python3
"""
Test script to verify IR player filtering is working correctly.
"""

from bench_scorer import BenchScorer
from config import config
import json

def test_ir_filtering():
    """Test that IR players are properly excluded from bench scoring."""
    
    print("Testing IR player filtering...")
    print("=" * 50)
    
    # Initialize bench scorer
    scorer = BenchScorer(config.league_id)
    
    # Test week 1 (should have some bench points)
    print("\nTesting Week 1:")
    week1_results = scorer.process_week_bench_scores(1)
    
    for result in week1_results:
        print(f"Team: {result.team_name} (Roster {result.roster_id})")
        print(f"  Bench Points: {result.total_bench_points}")
        print(f"  Bench Players: {result.bench_player_count}")
        
        # Show individual bench players
        if result.bench_players:
            print("  Players:")
            for player in result.bench_players:
                print(f"    {player.player_name} ({player.position}): {player.points} pts")
        else:
            print("  No bench players found")
        print()
    
    # Test week 2 (current week with low scores)
    print("\nTesting Week 2:")
    week2_results = scorer.process_week_bench_scores(2)
    
    for result in week2_results:
        print(f"Team: {result.team_name} (Roster {result.roster_id})")
        print(f"  Bench Points: {result.total_bench_points}")
        print(f"  Bench Players: {result.bench_player_count}")
        
        # Show individual bench players
        if result.bench_players:
            print("  Players:")
            for player in result.bench_players:
                print(f"    {player.player_name} ({player.position}): {player.points} pts")
        else:
            print("  No bench players found")
        print()

def debug_specific_roster():
    """Debug a specific roster to see IR vs bench breakdown."""
    
    print("\nDebugging specific roster (Roster 1)...")
    print("=" * 50)
    
    scorer = BenchScorer(config.league_id)
    
    # Get roster data
    rosters = scorer.league.get_rosters()
    roster_1 = None
    for roster in rosters:
        if roster.get('roster_id') == 1:
            roster_1 = roster
            break
    
    if roster_1:
        print("Roster 1 breakdown:")
        print(f"All players: {len(roster_1.get('players', []))}")
        print(f"Starters: {len(roster_1.get('starters', []))}")
        print(f"Reserve (IR): {len(roster_1.get('reserve', []))}")
        
        players = roster_1.get('players', [])
        starters = roster_1.get('starters', [])
        reserve = roster_1.get('reserve', [])
        
        print(f"\nAll players: {players}")
        print(f"Starters: {starters}")
        print(f"Reserve (IR): {reserve}")
        
        # Calculate bench using old method (includes IR)
        old_bench = list(set(players) - set(starters))
        print(f"\nOld method (includes IR): {len(old_bench)} bench players")
        print(f"Old bench players: {old_bench}")
        
        # Calculate bench using new method (excludes IR)
        new_bench = scorer.identify_bench_players(players, starters, reserve)
        print(f"\nNew method (excludes IR): {len(new_bench)} bench players")
        print(f"New bench players: {new_bench}")
        
        # Show the difference
        ir_players_in_old = set(old_bench) & set(reserve)
        print(f"\nIR players that were incorrectly included in old method: {list(ir_players_in_old)}")

if __name__ == "__main__":
    test_ir_filtering()
    debug_specific_roster()
