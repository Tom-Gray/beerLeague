# Backend (Legacy/Preserved)

⚠️ **This backend is no longer required for the dashboard deployment.**

The Beer League Dashboard has been converted to a static site that runs without a backend. This Flask API code is preserved for reference or future use if you need dynamic functionality.

## Current Status

- **Not Required**: The dashboard now uses static JSON files
- **Preserved**: All code remains intact for future reference
- **Alternative**: Use this if you prefer a dynamic backend over static deployment

## Original Flask API

This directory contains the original Flask-based backend that provided:

- RESTful API endpoints for dashboard data
- SQLite database for data storage
- CSV file processing and data loading
- CORS support for frontend integration

## Files Overview

- `app.py` - Main Flask application
- `models.py` - Database models (SQLAlchemy)
- `database.py` - Database initialization
- `config.py` - Configuration settings
- `api/` - API endpoint modules
- `services/` - Data processing services

## If You Want to Use the Backend

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize database:**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

5. **Load data:**
   ```bash
   python -c "from services.data_loader import load_all_data; load_all_data()"
   ```

6. **Run server:**
   ```bash
   python app.py
   ```

### API Endpoints

- `GET /api/standings/season` - Season standings
- `GET /api/matchups/` - All matchups  
- `GET /api/analytics/league-stats` - League statistics
- `GET /api/analytics/weekly-trends` - Weekly trends

### Frontend Integration

If using this backend, modify the frontend to use API calls instead of static JSON files:

```javascript
// Replace static imports with API calls
const response = await fetch('http://localhost:5000/api/standings/season');
const standings = await response.json();
```

## Why Static is Better

The static approach offers several advantages:

- ✅ **Free hosting** on GitHub Pages
- ✅ **No server maintenance** required
- ✅ **Faster loading** with CDN
- ✅ **More reliable** (no backend to fail)
- ✅ **Easier deployment** (just upload files)

## Migration Back to Dynamic

If you need to revert to the backend:

1. **Restore API calls** in frontend components
2. **Remove static data processing** from build
3. **Set up backend** following instructions above
4. **Deploy backend** to a service like Heroku or Railway

## Support

This backend code is preserved as-is. For the current static implementation, see the main README.md in the parent directory.
