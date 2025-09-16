import React, { useState, useEffect } from 'react';
import './App.css';
import StandingsTable from './components/StandingsTable';
import MatchupsList from './components/MatchupsList';
import AnalyticsCharts from './components/AnalyticsCharts';

const DATA_BASE_URL = '/data';

function App() {
  const [activeTab, setActiveTab] = useState('standings');
  const [standings, setStandings] = useState([]);
  const [matchups, setMatchups] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [standingsRes, matchupsRes, analyticsRes] = await Promise.all([
        fetch(`${DATA_BASE_URL}/standings.json`),
        fetch(`${DATA_BASE_URL}/matchups.json`),
        fetch(`${DATA_BASE_URL}/analytics.json`)
      ]);
      
      // Check if all requests were successful
      if (!standingsRes.ok || !matchupsRes.ok || !analyticsRes.ok) {
        throw new Error('Failed to fetch data files');
      }
      
      const [standingsData, matchupsData, analyticsData] = await Promise.all([
        standingsRes.json(),
        matchupsRes.json(),
        analyticsRes.json()
      ]);
      
      setStandings(standingsData);
      setMatchups(matchupsData);
      setAnalytics(analyticsData);
    } catch (err) {
      setError('Failed to load data. Please make sure the data files are available.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    if (loading) {
      return <div className="loading">Loading...</div>;
    }

    if (error) {
      return (
        <div className="error">
          <p>{error}</p>
          <button onClick={fetchData}>Retry</button>
        </div>
      );
    }

    switch (activeTab) {
      case 'standings':
        return <StandingsTable standings={standings} />;
      case 'matchups':
        return <MatchupsList matchups={matchups} />;
      case 'analytics':
        return <AnalyticsCharts analytics={analytics} />;
      default:
        return <StandingsTable standings={standings} />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏈 Beer League Bench Scoring Dashboard</h1>
        <nav className="nav-tabs">
          <button 
            className={activeTab === 'standings' ? 'active' : ''}
            onClick={() => setActiveTab('standings')}
          >
            Standings
          </button>
          <button 
            className={activeTab === 'matchups' ? 'active' : ''}
            onClick={() => setActiveTab('matchups')}
          >
            Matchups
          </button>
          <button 
            className={activeTab === 'analytics' ? 'active' : ''}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </button>
        </nav>
        <button className="refresh-btn" onClick={fetchData}>
          Refresh Data
        </button>
      </header>

      <main className="App-main">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
