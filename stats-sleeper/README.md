# Beer League Bench Scoring System

A comprehensive fantasy football bench scoring system for Sleeper leagues. Track and compete on bench player performance with detailed weekly matchups, season standings, and comprehensive reporting.

## Features

- **Weekly Bench Scoring**: Automatically calculate bench points for each team
- **Head-to-Head Matchups**: Create bench-only matchups based on your league's schedule
- **Season Standings**: Track wins, losses, and performance statistics
- **Comprehensive Reports**: Generate detailed text and HTML reports
- **Data Export**: Save results to CSV for further analysis
- **Player Lookup**: Detailed player information with position and team data

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd stats-sleeper

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure your league:

```bash
cp .env.example .env
```

Edit `.env` with your league information:

```bash
# Your Sleeper league ID (required)
SLEEPER_LEAGUE_ID=your_league_id_here

# Data directory for output files (optional)
DATA_DIR=data

# Player cache settings (optional)
CACHE_PLAYERS=true
PLAYER_CACHE_FILE=data/player_cache.json
```

### 3. Basic Usage

```bash
# Process current week
python main_bench_scoring.py --week current

# Process entire season
python main_bench_scoring.py --season

# Generate HTML report
python main_bench_scoring.py --season --html
```

## Usage Examples

### Process Specific Week
```bash
# Process week 5
python main_bench_scoring.py --week 5

# Process current week with verbose output
python main_bench_scoring.py --week current --verbose
```

### Process Multiple Weeks
```bash
# Process entire season so far
python main_bench_scoring.py --season

# Process weeks 1-10
python main_bench_scoring.py --start-week 1 --end-week 10
```

### Generate Reports
```bash
# Generate reports from existing data
python main_bench_scoring.py --reports-only

# Generate HTML report for season
python main_bench_scoring.py --season --html

# Quiet mode (minimal output)
python main_bench_scoring.py --season --quiet
```

### Custom Output Directory
```bash
# Save to custom directory
python main_bench_scoring.py --season --output-dir /path/to/output
```

## Output Files

The system generates several types of output files:

### CSV Files
- `weekly_results_TIMESTAMP.csv` - Detailed weekly bench results
- `weekly_matchups_TIMESTAMP.csv` - Head-to-head matchup results  
- `season_standings_TIMESTAMP.csv` - Season standings and statistics

### Report Files
- `season_summary_TIMESTAMP.txt` - Text-based season summary
- `week_N_report_TIMESTAMP.txt` - Individual weekly reports
- `season_report_TIMESTAMP.html` - HTML season report (with --html flag)

### Data Structure

#### Weekly Results CSV
```csv
week,roster_id,owner_id,team_name,total_bench_points,bench_player_count,date_recorded,bench_players_detail
1,1,user123,Team Name,45.67,6,2024-09-10T10:30:00,"[{""player_id"":""123"",""name"":""Player Name"",""position"":""RB"",""team"":""LAR"",""points"":12.5}]"
```

#### Matchup Results CSV
```csv
week,matchup_id,team1_roster_id,team1_name,team1_bench_points,team2_roster_id,team2_name,team2_bench_points,winner_roster_id,margin_of_victory,date_recorded
1,1,1,Team A,45.67,2,Team B,38.23,1,7.44,2024-09-10T10:30:00
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SLEEPER_LEAGUE_ID` | Your Sleeper league ID | None | Yes |
| `DATA_DIR` | Output directory for files | `data` | No |
| `CACHE_PLAYERS` | Enable player info caching | `true` | No |
| `PLAYER_CACHE_FILE` | Player cache file location | `data/player_cache.json` | No |

### Finding Your League ID

1. Go to your league on Sleeper.app
2. Look at the URL: `https://sleeper.app/leagues/LEAGUE_ID/team`
3. The `LEAGUE_ID` is the number in the URL

## Command Line Options

```
usage: main_bench_scoring.py [-h] [--week WEEK | --season] [--start-week START_WEEK] 
                            [--end-week END_WEEK] [--output-dir OUTPUT_DIR] [--html] 
                            [--reports-only] [--quiet] [--verbose] [--league-id LEAGUE_ID]

Beer League Bench Scoring System

optional arguments:
  -h, --help            show this help message and exit
  --week WEEK           Process specific week (number or "current")
  --season              Process entire season so far
  --start-week START_WEEK
                        Start week for processing (default: 1)
  --end-week END_WEEK   End week for processing (default: current week)
  --output-dir OUTPUT_DIR
                        Output directory for files (default: data)
  --html                Generate HTML report
  --reports-only        Generate reports from existing data without processing new weeks
  --quiet               Suppress output except errors
  --verbose             Verbose output
  --league-id LEAGUE_ID
                        Sleeper league ID (default: from config)
```

## How It Works

### Bench Scoring Logic

1. **Fetch Matchup Data**: Gets weekly matchup data from Sleeper API
2. **Identify Bench Players**: Compares roster players vs. starters to find bench players
3. **Calculate Points**: Sums fantasy points for all bench players
4. **Create Matchups**: Pairs teams based on actual league matchups
5. **Determine Winners**: Compares bench points to determine matchup winners

### Scoring Rules

- **Bench Players**: Any rostered player not in the starting lineup
- **Points**: Uses standard Sleeper fantasy scoring
- **Matchups**: Based on your league's actual weekly matchups
- **Tiebreaker**: In case of tie, first team listed wins

### Season Standings

Teams are ranked by:
1. Win percentage (primary)
2. Total bench points (tiebreaker)

## API Dependencies

This system uses the [Sleeper API](https://docs.sleeper.app/) via the [sleeper-api-wrapper](https://github.com/SwapnikKatkoori/sleeper-api-wrapper) Python package.

### Rate Limiting

The system includes built-in delays to respect Sleeper's API rate limits:
- 0.5 second delay between week processing
- Error handling for API failures
- Automatic retries for transient errors

## Troubleshooting

### Common Issues

**"Configuration error: SLEEPER_LEAGUE_ID is required"**
- Make sure you've set `SLEEPER_LEAGUE_ID` in your `.env` file

**"No matchups found for week X"**
- Week may not have started yet or league may be inactive
- Verify your league ID is correct

**"Error getting current week"**
- API connection issue or NFL season not active
- Try specifying a specific week number

**"No existing data files found"**
- When using `--reports-only`, make sure you've processed some weeks first

### Debug Mode

Run with `--verbose` flag for detailed output:

```bash
python main_bench_scoring.py --week current --verbose
```

### Manual Testing

Test individual components:

```bash
# Test league connection
python get_matchups.py YOUR_LEAGUE_ID

# Test roster data
python get_rosters.py YOUR_LEAGUE_ID

# Test player lookup
python -c "from player_lookup import lookup_player_info; print(lookup_player_info('4046'))"
```

## Development

### Project Structure

```
stats-sleeper/
├── main_bench_scoring.py      # Main entry point
├── bench_scorer.py            # Core scoring logic
├── bench_data_manager.py      # Data persistence
├── bench_reporter.py          # Report generation
├── config.py                  # Configuration management
├── player_lookup.py           # Player information
├── get_matchups.py           # Matchup data fetching
├── get_rosters.py            # Roster data fetching
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── data/                    # Output directory
```

### Adding Features

The modular design makes it easy to extend:

- **New scoring rules**: Modify `BenchScorer` class
- **Additional reports**: Extend `BenchReporter` class  
- **New data formats**: Add methods to `BenchDataManager`
- **Custom analysis**: Create new scripts using the core classes

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your configuration and league ID
3. Test with `--verbose` flag for detailed error information

## Contributing

Contributions welcome! Areas for improvement:
- Additional report formats
- Enhanced player statistics
- Web interface
- Mobile notifications
- Integration with other fantasy platforms
