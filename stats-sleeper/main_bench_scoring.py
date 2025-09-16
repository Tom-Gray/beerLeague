#!/usr/bin/env python3
"""
Main entry point for the Beer League bench scoring system.
"""
import argparse
import sys
from typing import Optional
from datetime import datetime

from bench_scorer import BenchScorer
from bench_data_manager import BenchDataManager
from bench_reporter import BenchReporter
from config import config
from get_matchups import get_current_week

def main():
    """Main entry point with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Beer League Bench Scoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process current week only
  python main_bench_scoring.py --week current
  
  # Process specific week
  python main_bench_scoring.py --week 5
  
  # Process entire season so far
  python main_bench_scoring.py --season
  
  # Process week range
  python main_bench_scoring.py --start-week 1 --end-week 10
  
  # Generate reports only (no processing)
  python main_bench_scoring.py --reports-only
  
  # Export HTML report
  python main_bench_scoring.py --season --html
        """
    )
    
    # Week/Season options
    week_group = parser.add_mutually_exclusive_group()
    week_group.add_argument(
        '--week', 
        type=str, 
        help='Process specific week (number or "current")'
    )
    week_group.add_argument(
        '--season', 
        action='store_true', 
        help='Process entire season so far'
    )
    
    # Week range options
    parser.add_argument(
        '--start-week', 
        type=int, 
        default=1, 
        help='Start week for processing (default: 1)'
    )
    parser.add_argument(
        '--end-week', 
        type=int, 
        help='End week for processing (default: current week)'
    )
    
    # Output options
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default=config.data_dir,
        help=f'Output directory for files (default: {config.data_dir})'
    )
    parser.add_argument(
        '--html', 
        action='store_true', 
        help='Generate HTML report'
    )
    parser.add_argument(
        '--reports-only', 
        action='store_true', 
        help='Generate reports from existing data without processing new weeks'
    )
    
    # Display options
    parser.add_argument(
        '--quiet', 
        action='store_true', 
        help='Suppress output except errors'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Verbose output'
    )
    
    # League options
    parser.add_argument(
        '--league-id', 
        type=str, 
        default=config.league_id,
        help=f'Sleeper league ID (default: {config.league_id})'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1
    
    # Initialize components
    scorer = BenchScorer(args.league_id)
    data_manager = BenchDataManager(args.output_dir)
    reporter = BenchReporter(data_manager)
    
    if not args.quiet:
        print("🏈 Beer League Bench Scoring System")
        print("=" * 40)
        print(f"League ID: {args.league_id}")
        print(f"Output Directory: {args.output_dir}")
        print()
    
    try:
        # Handle reports-only mode
        if args.reports_only:
            return generate_reports_only(data_manager, reporter, args)
        
        # Determine weeks to process
        weeks_to_process = determine_weeks_to_process(args, scorer)
        if not weeks_to_process:
            print("No weeks to process")
            return 1
        
        if not args.quiet:
            print(f"Processing weeks: {weeks_to_process}")
            print()
        
        # Process weeks
        all_results = []
        all_matchups = []
        
        for week in weeks_to_process:
            if args.verbose:
                print(f"Processing week {week}...")
            
            try:
                weekly_results, matchups = scorer.fetch_week_data(week)
                all_results.extend(weekly_results)
                all_matchups.extend(matchups)
                
                if not args.quiet and not args.verbose:
                    print(f"Week {week}: {len(weekly_results)} teams, {len(matchups)} matchups")
                
            except Exception as e:
                print(f"Error processing week {week}: {e}")
                continue
        
        if not all_results and not all_matchups:
            print("No data processed")
            return 1
        
        # Save data
        if not args.quiet:
            print(f"\nSaving data...")
        
        data_manager.save_results(all_results, all_matchups)
        
        # Generate reports
        if not args.quiet:
            print("Generating reports...")
        
        generate_reports(all_results, all_matchups, data_manager, reporter, args)
        
        if not args.quiet:
            print("\n✅ Processing complete!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def determine_weeks_to_process(args, scorer: BenchScorer) -> list:
    """Determine which weeks to process based on arguments."""
    if args.week:
        if args.week.lower() == 'current':
            current_week = get_current_week()
            if current_week:
                return [current_week]
            else:
                print("Could not determine current week")
                return []
        else:
            try:
                week_num = int(args.week)
                return [week_num]
            except ValueError:
                print(f"Invalid week number: {args.week}")
                return []
    
    elif args.season:
        return scorer.get_season_weeks()
    
    else:
        # Use start-week and end-week
        end_week = args.end_week
        if end_week is None:
            current_week = get_current_week()
            end_week = current_week if current_week else args.start_week
        
        return list(range(args.start_week, end_week + 1))

def generate_reports_only(data_manager: BenchDataManager, reporter: BenchReporter, args) -> int:
    """Generate reports from existing data."""
    try:
        # Look for most recent data files
        import os
        import glob
        
        data_dir = args.output_dir
        
        # Find most recent results and matchups files
        results_files = glob.glob(os.path.join(data_dir, "weekly_results_*.csv"))
        matchups_files = glob.glob(os.path.join(data_dir, "weekly_matchups_*.csv"))
        
        if not results_files and not matchups_files:
            print("No existing data files found")
            return 1
        
        # Load most recent files
        results = []
        matchups = []
        
        if results_files:
            latest_results_file = max(results_files, key=os.path.getctime)
            filename = os.path.basename(latest_results_file)
            results = data_manager.load_historical_data(filename)
            print(f"Loaded {len(results)} results from {filename}")
        
        if matchups_files:
            latest_matchups_file = max(matchups_files, key=os.path.getctime)
            filename = os.path.basename(latest_matchups_file)
            matchups = data_manager.load_matchup_history(filename)
            print(f"Loaded {len(matchups)} matchups from {filename}")
        
        # Generate reports
        generate_reports(results, matchups, data_manager, reporter, args)
        
        print("✅ Reports generated successfully!")
        return 0
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        return 1

def generate_reports(results, matchups, data_manager: BenchDataManager, reporter: BenchReporter, args):
    """Generate all reports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate season standings
    standings = data_manager.calculate_season_standings(results, matchups)
    
    if standings:
        # Text reports
        season_summary = reporter.create_season_summary(standings)
        print("\n" + season_summary)
        
        # Save season summary to file
        summary_filename = f"season_summary_{timestamp}.txt"
        summary_path = data_manager.get_file_path(summary_filename)
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(season_summary)
        print(f"Season summary saved to {summary_path}")
        
        # Export JSON data for dashboard (replaces CSV export)
        from json_exporter import export_dashboard_data
        export_dashboard_data(results, matchups, standings, data_manager.data_dir)
        
        # Generate HTML report if requested
        if args.html:
            html_filename = f"season_report_{timestamp}.html"
            reporter.export_html_report(standings, html_filename)
    
    # Generate weekly reports for recent weeks
    if results:
        recent_weeks = sorted(set(r.week for r in results))[-3:]  # Last 3 weeks
        
        for week in recent_weeks:
            week_results = [r for r in results if r.week == week]
            week_matchups = [m for m in matchups if m.week == week]
            
            if week_results or week_matchups:
                weekly_report = reporter.create_weekly_report(week, week_results, week_matchups)
                
                # Save weekly report
                weekly_filename = f"week_{week}_report_{timestamp}.txt"
                weekly_path = data_manager.get_file_path(weekly_filename)
                with open(weekly_path, 'w', encoding='utf-8') as f:
                    f.write(weekly_report)
                
                if args.verbose:
                    print(f"Week {week} report saved to {weekly_path}")

if __name__ == "__main__":
    sys.exit(main())
