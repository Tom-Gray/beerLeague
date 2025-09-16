#!/usr/bin/env python3
"""
Test script to validate the bench scoring system components.
"""
import sys
import os
from typing import List, Dict, Any
import traceback

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        import config
        print("✓ config module imported")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from get_matchups import get_current_week, get_matchups_for_week, get_league_info
        print("✓ get_matchups functions imported")
    except ImportError as e:
        print(f"✗ Failed to import get_matchups: {e}")
        return False
    
    try:
        from get_rosters import get_roster_owners, get_users_mapping
        print("✓ get_rosters functions imported")
    except ImportError as e:
        print(f"✗ Failed to import get_rosters: {e}")
        return False
    
    try:
        from player_lookup import lookup_player_info, PlayerInfo
        print("✓ player_lookup functions imported")
    except ImportError as e:
        print(f"✗ Failed to import player_lookup: {e}")
        return False
    
    try:
        from bench_scorer import BenchScorer, WeeklyBenchResult, BenchMatchup
        print("✓ bench_scorer classes imported")
    except ImportError as e:
        print(f"✗ Failed to import bench_scorer: {e}")
        return False
    
    try:
        from bench_data_manager import BenchDataManager
        print("✓ bench_data_manager imported")
    except ImportError as e:
        print(f"✗ Failed to import bench_data_manager: {e}")
        return False
    
    try:
        from bench_reporter import BenchReporter
        print("✓ bench_reporter imported")
    except ImportError as e:
        print(f"✗ Failed to import bench_reporter: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config import config
        
        # Test that config object exists
        print(f"✓ Config object created")
        
        # Test required attributes
        if hasattr(config, 'league_id'):
            print(f"✓ league_id attribute exists: {config.league_id}")
        else:
            print("✗ league_id attribute missing")
            return False
        
        if hasattr(config, 'data_dir'):
            print(f"✓ data_dir attribute exists: {config.data_dir}")
        else:
            print("✗ data_dir attribute missing")
            return False
        
        # Test validation method
        if hasattr(config, 'validate_config'):
            print("✓ validate_config method exists")
        else:
            print("✗ validate_config method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_api_connection():
    """Test basic API connectivity."""
    print("\nTesting API connection...")
    
    try:
        from get_matchups import get_current_week
        
        current_week = get_current_week()
        if current_week:
            print(f"✓ API connection successful - Current week: {current_week}")
            return True
        else:
            print("⚠ API connection issue - Could not get current week")
            return False
            
    except Exception as e:
        print(f"✗ API connection test failed: {e}")
        return False

def test_player_lookup():
    """Test player lookup functionality."""
    print("\nTesting player lookup...")
    
    try:
        from player_lookup import lookup_player_info
        
        # Test with a known player ID (Josh Allen)
        test_player_id = "4046"
        player_info = lookup_player_info(test_player_id)
        
        if player_info:
            print(f"✓ Player lookup successful: {player_info.name} ({player_info.position})")
            return True
        else:
            print(f"⚠ Player lookup returned None for ID {test_player_id}")
            return False
            
    except Exception as e:
        print(f"✗ Player lookup test failed: {e}")
        return False

def test_data_structures():
    """Test data structure creation."""
    print("\nTesting data structures...")
    
    try:
        from bench_scorer import BenchPlayer, WeeklyBenchResult, BenchMatchup
        from datetime import datetime
        
        # Test BenchPlayer creation
        bench_player = BenchPlayer(
            player_id="123",
            player_name="Test Player",
            position="RB",
            team="LAR",
            points=15.5,
            week=1,
            roster_id=1,
            owner_id="owner123"
        )
        print("✓ BenchPlayer creation successful")
        
        # Test WeeklyBenchResult creation
        weekly_result = WeeklyBenchResult(
            week=1,
            roster_id=1,
            owner_id="owner123",
            team_name="Test Team",
            bench_players=[bench_player],
            total_bench_points=15.5,
            bench_player_count=1,
            date_recorded=datetime.now()
        )
        print("✓ WeeklyBenchResult creation successful")
        
        # Test BenchMatchup creation
        bench_matchup = BenchMatchup(
            week=1,
            matchup_id=1,
            team1_roster_id=1,
            team1_name="Team A",
            team1_bench_points=15.5,
            team2_roster_id=2,
            team2_name="Team B",
            team2_bench_points=12.3,
            winner_roster_id=1,
            margin_of_victory=3.2,
            date_recorded=datetime.now()
        )
        print("✓ BenchMatchup creation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Data structure test failed: {e}")
        return False

def test_bench_scorer_init():
    """Test BenchScorer initialization."""
    print("\nTesting BenchScorer initialization...")
    
    try:
        from bench_scorer import BenchScorer
        from config import config
        
        # Test with default league ID
        if config.league_id and config.league_id != "your_league_id_here":
            scorer = BenchScorer(config.league_id)
            print("✓ BenchScorer initialized with config league ID")
            return True
        else:
            # Test with dummy league ID
            scorer = BenchScorer("123456789")
            print("✓ BenchScorer initialized with test league ID")
            return True
            
    except Exception as e:
        print(f"✗ BenchScorer initialization failed: {e}")
        return False

def test_data_manager():
    """Test data manager functionality."""
    print("\nTesting data manager...")
    
    try:
        from bench_data_manager import BenchDataManager
        
        # Test initialization
        data_manager = BenchDataManager("test_data")
        print("✓ BenchDataManager initialized")
        
        # Test directory creation
        if os.path.exists("test_data"):
            print("✓ Data directory created")
        else:
            print("✗ Data directory not created")
            return False
        
        # Clean up test directory
        try:
            os.rmdir("test_data")
            print("✓ Test directory cleaned up")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"✗ Data manager test failed: {e}")
        return False

def test_reporter():
    """Test reporter functionality."""
    print("\nTesting reporter...")
    
    try:
        from bench_reporter import BenchReporter
        from bench_data_manager import BenchDataManager
        
        # Test initialization
        data_manager = BenchDataManager("test_data")
        reporter = BenchReporter(data_manager)
        print("✓ BenchReporter initialized")
        
        # Test empty report generation
        empty_report = reporter.create_season_summary([])
        if "No season data available" in empty_report:
            print("✓ Empty report generation works")
        else:
            print("✗ Empty report generation failed")
            return False
        
        # Clean up
        try:
            os.rmdir("test_data")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"✗ Reporter test failed: {e}")
        return False

def test_main_script():
    """Test main script can be imported."""
    print("\nTesting main script...")
    
    try:
        import main_bench_scoring
        print("✓ Main script imported successfully")
        
        # Test that main function exists
        if hasattr(main_bench_scoring, 'main'):
            print("✓ Main function exists")
        else:
            print("✗ Main function missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Main script test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\nTesting dependencies...")
    
    required_packages = [
        'requests',
        'sleeper_wrapper',
        'python-dotenv',
        'tabulate',
        'jinja2',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sleeper_wrapper':
                import sleeper_wrapper
            elif package == 'python-dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✓ {package} available")
        except ImportError:
            print(f"✗ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def run_all_tests():
    """Run all tests and return overall result."""
    print("🏈 Beer League Bench Scoring System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("API Connection", test_api_connection),
        ("Player Lookup", test_player_lookup),
        ("Data Structures", test_data_structures),
        ("BenchScorer Init", test_bench_scorer_init),
        ("Data Manager", test_data_manager),
        ("Reporter", test_reporter),
        ("Main Script", test_main_script),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("-" * 20)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! System is ready to use.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
