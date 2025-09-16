# Beer League Bench Scoring System

A comprehensive fantasy football bench scoring system for Sleeper leagues, featuring data collection scripts and a static web dashboard for tracking and visualizing bench player performance.

## 🏈 Overview

This system fetches weekly matchup data from Sleeper, calculates bench player scores, and provides both command-line reports and a modern web dashboard to track which teams have the best bench players each week.

## 📁 Project Structure

```
beerLeague/
├── stats-sleeper/          # Data collection scripts
├── beer-league-dashboard/  # Static web application
│   ├── frontend/          # React web interface (static build)
│   ├── backend/           # Legacy Flask API (preserved)
│   ├── build-static-data.js # CSV to JSON processor
│   └── .github/workflows/ # GitHub Actions deployment
└── stats-yahoo/          # Legacy Yahoo Fantasy tools
```

---

## 🔧 Data Collection Scripts (`stats-sleeper/`)

### Features

- **Sleeper API Integration**: Fetches live data from your Sleeper fantasy league
- **Bench Score Calculation**: Automatically calculates points for all bench players
- **Weekly Matchup Analysis**: Determines bench scoring winners for each matchup
- **Multiple Output Formats**: Generates CSV files, text reports, and JSON data
- **Season Tracking**: Maintains cumulative standings across all weeks
- **Player Caching**: Optimizes API calls by caching player information

### Setup

1. **Install Dependencies**:
   ```bash
   cd stats-sleeper
   pip install -r requirements.txt
   ```

2. **Configure League Settings**:
   ```bash
   cp .env.example .env
   # Edit .env with your league details:
   # SLEEPER_LEAGUE_ID=your_league_id
   # SLEEPER_USERNAME=your_username
   ```

### Usage

**Run Complete Bench Scoring Analysis**:
```bash
python main_bench_scoring.py
```

**Individual Components**:
```bash
# Fetch matchup data only
python get_matchups.py

# Fetch roster data only  
python get_rosters.py

# Test system configuration
python test_system.py
```

### Generated Files

All output files are saved to `stats-sleeper/data/` with timestamps:

- **CSV Files**:
  - `weekly_results_YYYYMMDD_HHMMSS.csv` - Individual week results
  - `weekly_matchups_YYYYMMDD_HHMMSS.csv` - Head-to-head matchups
  - `season_standings_YYYYMMDD_HHMMSS.csv` - Cumulative season standings

- **Text Reports**:
  - `week_X_report_YYYYMMDD_HHMMSS.txt` - Detailed weekly summaries
  - `season_summary_YYYYMMDD_HHMMSS.txt` - Season overview

---

## 🌐 Static Web Dashboard (`beer-league-dashboard/`)

### What It Is

A modern React web application that provides:
- **Interactive Standings**: Leaderboard with rankings and statistics
- **Weekly Matchups**: Head-to-head bench scoring comparisons  
- **Analytics Dashboard**: Charts and visualizations of trends
- **Static Deployment**: No backend required - perfect for GitHub Pages
- **Responsive Design**: Works on desktop and mobile devices

### Quick Setup

1. **Install Dependencies**:
   ```bash
   cd beer-league-dashboard/frontend
   npm install
   ```

2. **Build Static Site**:
   ```bash
   npm run build:static
   ```

3. **Deploy to GitHub Pages**:
   - Push to GitHub repository
   - Enable GitHub Pages in repository settings
   - Point to `/beer-league-dashboard/frontend/build` folder

### Local Development

```bash
cd beer-league-dashboard/frontend
npm start
# View at http://localhost:3000
```

### Features

- **No Backend Required**: Uses pre-processed JSON files
- **Fast Loading**: ~160KB total size, CDN-optimized
- **Free Hosting**: Perfect for GitHub Pages
- **Automatic Updates**: GitHub Actions rebuilds on data changes
- **Mobile Responsive**: Works on all devices

---

## 🚀 Quick Start Guide

### Option 1: Static Deployment (Recommended)

1. **Configure Sleeper League**:
   ```bash
   cd stats-sleeper
   cp .env.example .env
   # Add your SLEEPER_LEAGUE_ID and SLEEPER_USERNAME
   ```

2. **Collect Initial Data**:
   ```bash
   python main_bench_scoring.py
   ```

3. **Build Static Dashboard**:
   ```bash
   cd ../beer-league-dashboard/frontend
   npm install
   npm run build:static
   ```

4. **Deploy to GitHub Pages**:
   - Push repository to GitHub
   - Enable Pages in repository settings
   - Select source: Deploy from branch, main, `/beer-league-dashboard/frontend/build`

5. **View Dashboard**: Your GitHub Pages URL (e.g., `username.github.io/repo-name`)

### Option 2: Local Development

1. **Follow steps 1-2 above**

2. **Start Development Server**:
   ```bash
   cd beer-league-dashboard/frontend
   npm start
   # View at http://localhost:3000
   ```

### Weekly Workflow

1. **Update Data**: Run `python main_bench_scoring.py` after games complete
2. **Rebuild Dashboard**: Run `npm run build:static` 
3. **Auto-Deploy**: Push to GitHub - Actions will rebuild and deploy automatically
4. **Share Results**: Dashboard URL is ready to share with league members

---

## 📊 Dashboard Features

### Standings Tab
- Team rankings with trophy icons
- Total bench points and weekly wins
- Best/worst weekly performances
- Color-coded performance tiers

### Matchups Tab  
- Week-by-week head-to-head comparisons
- Winner declarations for each matchup
- Historical matchup browsing
- Tie game identification

### Analytics Tab
- League performance statistics
- Weekly trend analysis with interactive charts
- Team performance comparisons
- Wins distribution visualization

---

## 🔄 Data Updates

### Manual Process
1. **Generate Data**: `python main_bench_scoring.py` in stats-sleeper
2. **Rebuild Site**: `npm run build:static` in frontend
3. **Deploy**: Push to GitHub or upload to hosting service

### Automated Process (GitHub Pages)
1. **Generate Data**: Run stats-sleeper scripts
2. **Commit Changes**: Push CSV files to repository
3. **Auto-Deploy**: GitHub Actions detects changes and rebuilds site
4. **Live Update**: Dashboard automatically updates with new data

---

## 🛠️ Deployment Options

### GitHub Pages (Free & Recommended)
- ✅ **Free hosting**
- ✅ **Automatic deployments** via GitHub Actions
- ✅ **CDN performance**
- ✅ **Custom domain support**

See `beer-league-dashboard/STATIC-DEPLOYMENT.md` for complete setup guide.

### Other Static Hosts
- **Netlify**: Connect GitHub repo, build command: `npm run build:static`
- **Vercel**: Import project, framework: React
- **Any Web Server**: Upload `build/` directory contents

---

## 🏗️ Legacy Backend (Preserved)

The original Flask API backend is preserved in `beer-league-dashboard/backend/` for reference or future use, but is **not required** for the static deployment.

**If you want to use the backend**:
1. Follow setup instructions in `beer-league-dashboard/backend/README.md`
2. Modify frontend to use API calls instead of static JSON files
3. Deploy backend to a service like Heroku or Railway

---

## 🛠️ Troubleshooting

**Common Issues**:

1. **"No data available"**: Run the data collection script first
2. **Build failures**: Ensure Node.js 14+ and check CSV file paths
3. **GitHub Pages not updating**: Check Actions tab for build status
4. **Missing dependencies**: Run `pip install -r requirements.txt` and `npm install`

**Debug Commands**:
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

---

## 📈 Performance & Benefits

### Static Site Advantages
- **Fast Loading**: No database queries or API calls
- **Reliable**: No backend infrastructure to fail
- **Scalable**: CDN handles any traffic load
- **Secure**: No server-side vulnerabilities
- **Cost-Effective**: Free hosting on GitHub Pages

### Technical Specs
- **Total Size**: ~160KB (gzipped)
- **Load Time**: <1 second on fast connections
- **Browser Support**: All modern browsers
- **Mobile Optimized**: Responsive design

---

## 🔮 Future Enhancements

- **Real-time Updates**: WebSocket integration for live scoring
- **Player Analytics**: Individual player performance tracking
- **Export Features**: PDF reports and data downloads
- **Mobile App**: React Native version
- **Multi-League Support**: Track multiple leagues simultaneously
- **Advanced Charts**: More detailed analytics and visualizations

---

*Built for fantasy football commissioners who want to add an extra layer of competition and engagement to their leagues!* 🏆

## 📚 Documentation

- **Main Setup**: This README
- **Dashboard Details**: `beer-league-dashboard/README.md`
- **Static Deployment**: `beer-league-dashboard/STATIC-DEPLOYMENT.md`
- **Frontend Guide**: `beer-league-dashboard/frontend/README.md`
- **Legacy Backend**: `beer-league-dashboard/backend/README.md`
- **Data Collection**: `stats-sleeper/README.md`
