#!/usr/bin/env python3
"""
Yahoo Fantasy League Data Extractor - Main Script

This is the main entry point for extracting historical data from Yahoo Fantasy leagues.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from yahoo_extractor import YahooFantasyExtractor
    from csv_exporter import CSVExporter
    from text_formatter import TextFormatter
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required files are in the same directory.")
    sys.exit(1)

def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('extraction.log')
        ]
    )

def check_credentials():
    """Check if Yahoo API credentials are configured."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ No .env file found!")
        print("\nTo set up Yahoo API credentials:")
        print("1. Run: python setup_auth.py")
        print("2. Follow the instructions to create a Yahoo Developer app")
        print("3. Run: python setup_auth.py --configure")
        return False
    
    # Load and check credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('YAHOO_CLIENT_ID')
    client_secret = os.getenv('YAHOO_CLIENT_SECRET')
    league_id = os.getenv('LEAGUE_ID')
    
    if not client_id or not client_secret:
        print("❌ Yahoo API credentials not found in .env file!")
        print("\nRun: python setup_auth.py --configure")
        return False
    
    if not league_id:
        print("❌ League ID not found in .env file!")
        return False
    
    print("✅ Credentials found!")
    print(f"   League ID: {league_id}")
    return True

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Extract historical data from Yahoo Fantasy leagues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Extract all data with default settings
  python main.py --verbose          # Run with detailed logging
  python main.py --output-dir ./my_data  # Save to custom directory
  python main.py --check-auth       # Check authentication setup
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='data',
        help='Output directory for CSV files (default: data)'
    )
    
    parser.add_argument(
        '--check-auth',
        action='store_true',
        help='Check authentication setup and exit'
    )
    
    parser.add_argument(
        '--league-id',
        help='Override league ID from environment'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("YAHOO FANTASY LEAGUE DATA EXTRACTOR")
    print("=" * 60)
    print()
    
    # Check authentication
    if not check_credentials():
        sys.exit(1)
    
    if args.check_auth:
        print("✅ Authentication setup is complete!")
        sys.exit(0)
    
    # Get league ID
    league_id = args.league_id or os.getenv('LEAGUE_ID')
    
    try:
        print(f"🏈 Initializing extractor for league {league_id}...")
        
        # Initialize extractor
        extractor = YahooFantasyExtractor(league_id)
        
        print("📊 Starting data extraction...")
        print("   This may take several minutes depending on league history...")
        print()
        
        # Extract all data
        rankings, highest_scores, lowest_scores = extractor.extract_all_data()
        
        print(f"✅ Data extraction complete!")
        print(f"   - Final rankings: {len(rankings)} records")
        print(f"   - Highest scores: {len(highest_scores)} records")
        print(f"   - Lowest scores: {len(lowest_scores)} records")
        print()
        
        # Export to CSV
        print("💾 Exporting data to CSV files...")
        
        exporter = CSVExporter(args.output_dir)
        csv_success = exporter.export_all_data(rankings, highest_scores, lowest_scores)
        
        if csv_success:
            print("✅ CSV export successful!")
            
            # Create summary report
            exporter.create_summary_report(rankings, highest_scores, lowest_scores)
        else:
            print("❌ CSV export failed!")
        
        # Export to text format
        print("\n📝 Exporting data to text files...")
        
        formatter = TextFormatter(args.output_dir)
        text_success = formatter.export_all_text_formats(rankings, highest_scores, lowest_scores)
        
        if text_success:
            print("✅ Text export successful!")
        else:
            print("❌ Text export failed!")
        
        # List exported files
        if csv_success or text_success:
            print("\n📁 Exported files:")
            if csv_success:
                exporter.list_exported_files()
            
            # List text files
            if text_success:
                text_files = Path(args.output_dir).glob("*.txt")
                for file in text_files:
                    print(f"   📄 {file}")
        
        print("\n🎉 Data extraction and export completed successfully!")
        print(f"\nFiles are available in: {Path(args.output_dir).absolute()}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        print(f"\n❌ Error: {e}")
        
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print("\nRun with --verbose for detailed error information")
        
        sys.exit(1)

if __name__ == '__main__':
    main()
