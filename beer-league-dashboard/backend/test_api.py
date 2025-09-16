#!/usr/bin/env python3
"""
Test script for the Beer League Dashboard API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import init_db
from services.data_loader import DataLoaderService
from config import Config

def test_api():
    """Test the API endpoints"""
    print("🍺 Beer League Dashboard API Test")
    print("=" * 50)
    
    # Create app
    app = create_app('development')
    
    with app.test_client() as client:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = client.get('/health')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.get_json()}")
        else:
            print(f"   Error: {response.data}")
        
        # Test data sync endpoint
        print("\n2. Testing data sync endpoint...")
        try:
            response = client.get('/api/sync')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Sync results: {data.get('results', {})}")
            else:
                print(f"   Error: {response.get_json()}")
        except Exception as e:
            print(f"   Error during sync: {e}")
        
        # Test API documentation
        print("\n3. Testing API documentation...")
        response = client.get('/docs/')
        print(f"   Swagger docs status: {response.status_code}")
        
        # Test standings endpoints
        print("\n4. Testing standings endpoints...")
        
        # Season standings
        response = client.get('/api/standings/season')
        print(f"   Season standings status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Found {len(data)} teams in standings")
        
        # Weekly standings
        response = client.get('/api/standings/weekly')
        print(f"   Weekly standings status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Found {len(data)} weekly results")
        
        # Test matchups endpoints
        print("\n5. Testing matchups endpoints...")
        
        response = client.get('/api/matchups/')
        print(f"   All matchups status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Found {len(data)} matchups")
        
        # Test analytics endpoints
        print("\n6. Testing analytics endpoints...")
        
        response = client.get('/api/analytics/league-stats')
        print(f"   League stats status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   League has {data.get('total_teams', 0)} teams, {data.get('total_weeks', 0)} weeks")
        
        response = client.get('/api/analytics/weekly-trends')
        print(f"   Weekly trends status: {response.status_code}")
        
        response = client.get('/api/analytics/performance-distribution')
        print(f"   Performance distribution status: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("✅ API test completed!")

def check_data_files():
    """Check if data files exist"""
    print("\n📁 Checking data files...")
    
    config = Config()
    data_dir = config.DATA_DIR
    
    print(f"   Data directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"   ❌ Data directory does not exist: {data_dir}")
        return False
    
    # Check for CSV files
    import glob
    weekly_files = glob.glob(os.path.join(data_dir, 'weekly_results_*.csv'))
    matchup_files = glob.glob(os.path.join(data_dir, 'weekly_matchups_*.csv'))
    
    print(f"   Weekly results files: {len(weekly_files)}")
    print(f"   Matchup files: {len(matchup_files)}")
    
    if weekly_files:
        print(f"   Latest weekly results: {os.path.basename(weekly_files[-1])}")
    if matchup_files:
        print(f"   Latest matchups: {os.path.basename(matchup_files[-1])}")
    
    return len(weekly_files) > 0 and len(matchup_files) > 0

if __name__ == '__main__':
    print("🚀 Starting Beer League Dashboard API Test")
    
    # Check data files first
    if not check_data_files():
        print("\n⚠️  Warning: No data files found. Run the stats-sleeper system first to generate data.")
        print("   The API will still work but will return empty results.")
    
    # Run API tests
    test_api()
    
    print("\n🎯 To start the development server, run:")
    print("   cd beer-league-dashboard/backend")
    print("   python app.py")
    print("\n📖 API documentation will be available at: http://localhost:5000/docs/")
