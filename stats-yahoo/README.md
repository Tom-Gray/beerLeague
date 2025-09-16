# Yahoo Fantasy League Data Extractor

A Python tool to extract historical data from Yahoo Fantasy NFL leagues and export it to CSV format for analysis and display.

## Features

- Extract final season rankings for all available years
- Extract highest weekly scores across all seasons
- Extract lowest weekly scores across all seasons
- Export data to clean CSV format
- Comprehensive error handling and logging
- Interactive setup for Yahoo Developer credentials

## Data Extracted

### Final Rankings (`final_rankings_by_season.csv`)
- Season year
- Final rank
- Team name
- Wins, losses, ties
- Points for/against
- Team key for reference

### Highest Scores (`highest_scores_by_season.csv`)
- Season year
- Week number
- Team name with highest score
- Points scored
- Team key for reference

### Lowest Scores (`lowest_scores_by_season.csv`)
- Season year
- Week number
- Team name with lowest score
- Points scored
- Team key for reference

## Setup Instructions

### 1. Install Dependencies

```bash
cd stats-yahoo
pip install -r requirements.txt
```

### 2. Set Up Yahoo Developer Credentials

First, get setup instructions:
```bash
python setup_auth.py
```

This will guide you through:
1. Creating a Yahoo Developer app at https://developer.yahoo.com/apps/
2. Getting your Client ID and Client Secret

Then configure your credentials:
```bash
python setup_auth.py --configure
```

### 3. Run the Extractor

Extract all available historical data:
```bash
python main.py
```

## Usage Options

### Basic Usage
```bash
python main.py                    # Extract all data with default settings
```

### Advanced Options
```bash
python main.py --verbose          # Run with detailed logging
python main.py --output-dir ./my_data  # Save to custom directory
python main.py --check-auth       # Check authentication setup
python main.py --league-id 123456 # Override league ID
```

## Configuration

The tool uses a `.env` file for configuration:

```env
# Yahoo Fantasy API Credentials
YAHOO_CLIENT_ID=your_client_id_here
YAHOO_CLIENT_SECRET=your_client_secret_here

# League Configuration
LEAGUE_ID=848590
```

## Output Files

All CSV files are saved to the `data/` directory (or custom directory specified):

- `final_rankings_by_season.csv` - Season-end standings
- `highest_scores_by_season.csv` - Weekly high scores
- `lowest_scores_by_season.csv` - Weekly low scores
- `extraction_summary.csv` - Summary of extracted data

## Error Handling

- Comprehensive logging to `extraction.log`
- Rate limiting to respect Yahoo API limits
- Graceful handling of missing seasons or weeks
- Detailed error messages with troubleshooting guidance

## Troubleshooting

### Authentication Issues
1. Ensure you've created a Yahoo Developer app
2. Check that your Client ID and Secret are correct
3. Verify the redirect URI is set to `http://localhost:8080`
4. Make sure Fantasy Sports permissions are enabled

### Data Extraction Issues
1. Run with `--verbose` flag for detailed logging
2. Check `extraction.log` for specific error messages
3. Verify your league ID is correct
4. Some older seasons may not be available via the API

### Rate Limiting
The tool includes built-in rate limiting, but if you encounter issues:
- The tool will automatically retry failed requests
- Consider running during off-peak hours
- Check Yahoo's API status page for service issues

## League ID

Your league ID (848590) is pre-configured. You can find your league ID in the Yahoo Fantasy URL:
`https://football.fantasysports.yahoo.com/f1/LEAGUE_ID/...`

## Requirements

- Python 3.7+
- Yahoo Developer account
- Active Yahoo Fantasy league participation (for authentication)

## File Structure

```
stats-yahoo/
├── requirements.txt          # Python dependencies
├── .env.example             # Template for credentials
├── setup_auth.py           # Interactive setup guide
├── yahoo_extractor.py      # Main extraction logic
├── csv_exporter.py         # CSV formatting and export
├── main.py                 # Entry point script
├── README.md               # This file
└── data/                   # CSV output files
    ├── final_rankings_by_season.csv
    ├── highest_scores_by_season.csv
    ├── lowest_scores_by_season.csv
    └── extraction_summary.csv
```

## Next Steps

Once you have the CSV files, you can:
1. Import them into your display website
2. Analyze the data with pandas or Excel
3. Create visualizations and charts
4. Build historical league statistics

The CSV format makes it easy to integrate with any web framework or data analysis tool.


## Creds

App ID
ScQV3IiM
Client ID (Consumer Key)
dj0yJmk9Q3R6bEV6TUJRaHFIJmQ9WVdrOVUyTlJWak5KYVUwbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWZi
Client Secret (Consumer Secret)
f311891f288cddd21926c2d6d27fb5f928d8da9e