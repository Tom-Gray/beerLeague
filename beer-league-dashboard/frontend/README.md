# Beer League Dashboard Frontend

A React-based static web application for visualizing fantasy football bench scoring statistics. Built with Create React App and optimized for static deployment.

## Features

- **Interactive Dashboard**: Standings, matchups, and analytics views
- **Static Data**: No backend required - uses pre-processed JSON files
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Fast Loading**: Optimized for performance and CDN delivery
- **GitHub Pages Ready**: Perfect for free static hosting

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000
```

### Production Build

```bash
# Build static site with data processing
npm run build:static

# The build/ directory contains the complete static site
```

## Available Scripts

### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000).
- Hot reloading enabled
- Lint errors shown in console
- Uses sample data for development

### `npm run build:static`
**Primary build command** - Creates optimized production build with data processing:
1. Processes CSV files from `../stats-sleeper/data/`
2. Generates JSON data files
3. Builds React application
4. Outputs complete static site to `build/`

### `npm run build`
Standard React build without data processing.
Use this if you've already processed data separately.

### `npm run build:data`
Processes CSV data only (without building React app).
Useful for updating data without full rebuild.

### `npm test`
Launches the test runner in interactive watch mode.

## Data Processing

The build process automatically converts CSV files to optimized JSON:

### Input (CSV files from stats-sleeper)
- `weekly_results_*.csv` - Team bench scoring by week
- `weekly_matchups_*.csv` - Head-to-head matchup results

### Output (JSON files in build/data/)
- `standings.json` - Team rankings and statistics
- `matchups.json` - Weekly matchup details
- `analytics.json` - League trends and performance metrics
- `teams.json` - Team information and rosters
- `weekly-results.json` - Raw weekly data

## Project Structure

```
src/
├── components/           # React components
│   ├── StandingsTable.js    # League standings view
│   ├── MatchupsList.js      # Weekly matchups view
│   └── AnalyticsCharts.js   # Charts and analytics
├── App.js               # Main application component
├── App.css              # Styling and responsive design
└── index.js             # Application entry point

public/
├── index.html           # HTML template
└── data/                # Generated JSON files (after build)

build/                   # Production build output
├── static/              # Bundled JS/CSS assets
├── data/                # Processed JSON data
└── index.html           # Production HTML
```

## Component Overview

### StandingsTable
- Displays team rankings based on bench scoring
- Shows total points, weekly wins, averages
- Sortable columns and responsive layout

### MatchupsList
- Weekly head-to-head bench scoring results
- Expandable player details
- Week filtering and navigation

### AnalyticsCharts
- Interactive charts using Recharts library
- League trends and performance metrics
- Responsive chart sizing

## Styling

- **CSS Framework**: Custom responsive CSS
- **Design**: Modern, clean interface with football theme
- **Colors**: Purple gradient header with clean white content areas
- **Mobile**: Fully responsive design for all screen sizes

## Data Flow

1. **CSV Generation**: stats-sleeper system creates CSV files
2. **Data Processing**: `build-static-data.js` converts CSV to JSON
3. **React Build**: Standard Create React App build process
4. **Static Output**: Complete site ready for hosting

## Deployment

### GitHub Pages
```bash
npm run build:static
# Upload build/ directory contents to GitHub Pages
```

### Netlify
- Build command: `npm run build:static`
- Publish directory: `build`

### Vercel
- Framework: React
- Build command: `npm run build:static`
- Output directory: `build`

## Development Tips

### Local Development
- Uses sample data when CSV files aren't available
- Hot reloading for rapid development
- Console shows data loading status

### Adding Features
1. Create new components in `src/components/`
2. Import and use in `App.js`
3. Add styling to `App.css`
4. Test with `npm start`

### Data Updates
- Rebuild with `npm run build:static` after CSV updates
- Use `npm run build:data` for data-only updates
- Check `build/data/` for generated JSON files

## Performance

### Optimizations
- Code splitting with React.lazy (if needed)
- Minified and compressed assets
- Optimized JSON data structure
- CDN-friendly static assets

### Bundle Analysis
```bash
npm run build:static
npx serve -s build
# Analyze network tab in browser dev tools
```

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile**: iOS Safari, Chrome Mobile
- **Features**: ES6+, Fetch API, CSS Grid/Flexbox

## Troubleshooting

### Build Issues
- Ensure Node.js 14+ is installed
- Check that `csv-parser` is installed in parent directory
- Verify CSV files exist in `../stats-sleeper/data/`

### Data Issues
- Run `npm run build:data` to test data processing
- Check console for data loading errors
- Verify JSON files are generated in `build/data/`

### Deployment Issues
- Ensure all files in `build/` are uploaded
- Check that hosting service serves `index.html` for all routes
- Verify data files are accessible at `/data/*.json`

## Learn More

- [Create React App Documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React Documentation](https://reactjs.org/)
- [Recharts Documentation](https://recharts.org/)

## Integration

This frontend is designed to work seamlessly with:
- **stats-sleeper**: Provides CSV data source
- **GitHub Actions**: Automated deployment workflow
- **Static Hosting**: GitHub Pages, Netlify, Vercel

For complete setup instructions, see the main README.md in the parent directory.
