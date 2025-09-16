# Beer League Bench Scoring Dashboard

A static web application for tracking and visualizing fantasy football bench player performance in your Sleeper league. Designed for easy deployment on GitHub Pages.

## Features

- **Standings Table**: View overall bench scoring rankings with total points, weekly wins, and performance metrics
- **Weekly Matchups**: Browse bench scoring matchups by week with head-to-head comparisons
- **Analytics Dashboard**: Interactive charts showing trends, team performance, and league statistics
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Static Data**: Automatically processes CSV files into optimized JSON for fast loading

## Architecture

### Static Site (Current)
- **React** frontend with functional components and hooks
- **Static JSON** data files generated from CSV sources
- **Recharts** for interactive data visualizations
- **Responsive CSS** with modern styling
- **No backend required** - perfect for GitHub Pages

### Legacy Backend (Preserved)
The original Flask API backend is preserved in the `/backend/` directory for reference or future use, but is not required for the static deployment.

## Prerequisites

- Node.js 14+
- npm or yarn
- Existing bench scoring data from the stats-sleeper system

## Quick Start

### 1. Install Dependencies

```bash
cd beer-league-dashboard/frontend
npm install
```

### 2. Build Static Site

```bash
# Build with automatic data processing
npm run build:static

# The static site will be in the build/ directory
```

### 3. Deploy

Upload the `build/` directory contents to any static hosting service:
- **GitHub Pages** (recommended - free)
- **Netlify**
- **Vercel**
- **Any web server**

## Development

### Local Development

```bash
cd beer-league-dashboard/frontend

# Start development server
npm start

# View at http://localhost:3000
```

### Data Processing

The build process automatically:
1. Reads CSV files from `../stats-sleeper/data/`
2. Processes team information, standings, and matchups
3. Generates optimized JSON files
4. Builds the React application

### Manual Data Update

```bash
# Process data only (without building React app)
cd beer-league-dashboard
node build-static-data.js

# Then rebuild the site
cd frontend
npm run build
```

## Data Requirements

The system expects CSV files in `../stats-sleeper/data/` with the following structure:

### weekly_results_*.csv
```csv
week,roster_id,team_name,total_bench_points,bench_player_count,date_recorded
1,123456,Team Alpha,45.2,8,2024-09-12
```

### weekly_matchups_*.csv
```csv
week,matchup_id,team1_roster_id,team1_bench_points,team2_roster_id,team2_bench_points,winner_roster_id,margin_of_victory,date_recorded
1,1,123456,45.2,789012,38.7,123456,6.5,2024-09-12
```

## Generated Data Files

The build process creates these JSON files in `build/data/`:

- **standings.json**: Team rankings and statistics
- **matchups.json**: Weekly matchup details with player info
- **analytics.json**: League trends and performance metrics
- **teams.json**: Team roster information
- **weekly-results.json**: Raw weekly performance data

## Deployment Options

### GitHub Pages (Recommended)

1. **Push to Repository**
   ```bash
   git add .
   git commit -m "Deploy static dashboard"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main`
   - Folder: `/beer-league-dashboard/frontend/build`

3. **Automatic Updates**
   - The included GitHub Actions workflow rebuilds on CSV changes
   - Just push updated data files to trigger deployment

### Other Hosting Services

**Netlify:**
- Build command: `cd beer-league-dashboard/frontend && npm run build:static`
- Publish directory: `beer-league-dashboard/frontend/build`

**Vercel:**
- Framework: React
- Root directory: `beer-league-dashboard/frontend`
- Build command: `npm run build:static`

## Build Commands

```bash
# Development
npm start                    # Start dev server

# Production
npm run build:static         # Build static site with data processing
npm run build               # Build React app only
npm run build:data          # Process CSV data only

# Testing
npm test                    # Run tests
```

## Performance

### Optimized for Speed
- **Total size**: ~160KB (gzipped)
- **Data files**: 5-10KB each
- **Fast loading**: No API calls or database queries
- **CDN friendly**: All assets cacheable

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Progressive enhancement

## Updating Data

### Workflow
1. **Generate new data**: Run your stats-sleeper system
2. **Rebuild site**: `npm run build:static`
3. **Deploy**: Push to GitHub or upload to hosting service

### Automation
The included GitHub Actions workflow automatically:
- Detects changes to CSV files
- Rebuilds the static site
- Deploys to GitHub Pages

## Troubleshooting

### Common Issues

**No data showing:**
- Ensure CSV files exist in `../stats-sleeper/data/`
- Check file naming matches pattern: `*_results_*.csv`, `*_matchups_*.csv`
- Verify data processing: `node build-static-data.js`

**Build failures:**
- Install csv-parser: `npm install csv-parser` (in root directory)
- Check Node.js version (requires 14+)
- Verify file paths are correct

**GitHub Pages not updating:**
- Check Actions tab for build status
- Ensure correct branch/folder selected in Pages settings
- Clear browser cache

### Debug Commands

```bash
# Test data processing
cd beer-league-dashboard
node build-static-data.js

# Check generated files
ls -la frontend/build/data/

# Test locally
cd frontend
npx serve -s build
```

## Integration with Stats-Sleeper

This dashboard works seamlessly with the stats-sleeper system:

1. **Run bench scoring collection** in stats-sleeper
2. **CSV files are generated** in `stats-sleeper/data/`
3. **Dashboard processes** CSV files automatically during build
4. **Static site** contains all processed data

## File Structure

```
beer-league-dashboard/
├── build-static-data.js          # CSV to JSON processor
├── .github/workflows/deploy.yml  # GitHub Actions deployment
├── STATIC-DEPLOYMENT.md          # Detailed deployment guide
├── README.md                     # This file
├── frontend/                     # React application
│   ├── build/                    # Generated static site
│   ├── src/                      # React source code
│   ├── package.json              # Dependencies and scripts
│   └── public/                   # Static assets
└── backend/                      # Legacy Flask API (preserved)
    └── ...                       # Not required for static deployment
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `npm run build:static`
5. Submit a pull request

## License

This project is part of the Beer League fantasy football tooling suite.
