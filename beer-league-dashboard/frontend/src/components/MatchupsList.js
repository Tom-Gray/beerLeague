import React, { useState } from 'react';

const MatchupsList = ({ matchups }) => {
  const [selectedWeek, setSelectedWeek] = useState('all');
  const [expandedMatchups, setExpandedMatchups] = useState(new Set());
  const [expandAll, setExpandAll] = useState(false);

  // Helper function to truncate long player names
  const truncateName = (name) => {
    if (name.length <= 12) return name;
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}. ${parts[parts.length - 1]}`;
    }
    return name.substring(0, 12) + '...';
  };

  // Helper functions for expand/collapse functionality
  const getMatchupId = (week, index) => `${week}-${index}`;
  
  const toggleMatchupExpansion = (matchupId) => {
    setExpandedMatchups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(matchupId)) {
        newSet.delete(matchupId);
      } else {
        newSet.add(matchupId);
      }
      return newSet;
    });
  };

  const toggleExpandAll = () => {
    if (expandAll) {
      setExpandedMatchups(new Set());
    } else {
      const allMatchupIds = new Set();
      Object.keys(matchupsByWeek).forEach(week => {
        matchupsByWeek[week].forEach((_, index) => {
          allMatchupIds.add(getMatchupId(week, index));
        });
      });
      setExpandedMatchups(allMatchupIds);
    }
    setExpandAll(!expandAll);
  };

  if (!matchups || matchups.length === 0) {
    return (
      <div className="no-data">
        <p>No matchup data available. Make sure you have bench scoring data loaded.</p>
      </div>
    );
  }

  // Get unique weeks for filter
  const weeks = [...new Set(matchups.map(m => m.week))].sort((a, b) => b - a);
  
  // Filter matchups by selected week
  const filteredMatchups = selectedWeek === 'all' 
    ? matchups 
    : matchups.filter(m => m.week === parseInt(selectedWeek));

  // Group matchups by week for display
  const matchupsByWeek = filteredMatchups.reduce((acc, matchup) => {
    if (!acc[matchup.week]) {
      acc[matchup.week] = [];
    }
    acc[matchup.week].push(matchup);
    return acc;
  }, {});

  return (
    <div className="matchups-container">
      <div className="matchups-header">
        <h2>Weekly Bench Matchups</h2>
        <div className="header-controls">
          <div className="week-filter">
            <label htmlFor="week-select">Filter by Week:</label>
            <select 
              id="week-select"
              value={selectedWeek} 
              onChange={(e) => setSelectedWeek(e.target.value)}
            >
              <option value="all">All Weeks</option>
              {weeks.map(week => (
                <option key={week} value={week}>Week {week}</option>
              ))}
            </select>
          </div>
          <button 
            className="expand-all-btn"
            onClick={toggleExpandAll}
          >
            {expandAll ? '📁 Collapse All' : '📂 Expand All'}
          </button>
        </div>
      </div>

      <div className="matchups-list">
        {Object.keys(matchupsByWeek)
          .sort((a, b) => b - a)
          .map(week => (
            <div key={week} className="week-section" style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '2px solid #e0e0e0' }}>
              <h3 style={{ marginBottom: '1rem', fontSize: '1.3em', fontWeight: 'bold', color: '#333' }}>Week {week}</h3>
              <div className="matchups-grid">
                {matchupsByWeek[week].map((matchup, index) => {
                  const team1Points = matchup.team1?.bench_points || 0;
                  const team2Points = matchup.team2?.bench_points || 0;
                  const team1Players = matchup.team1?.bench_players || [];
                  const team2Players = matchup.team2?.bench_players || [];
                  const matchupId = getMatchupId(week, index);
                  const isExpanded = expandedMatchups.has(matchupId);

                  return (
                    <div key={`${week}-${index}`} className="matchup-card">
                      <div className="matchup-header">
                        <div className={`team-header ${team1Points > team2Points ? 'winner' : ''}`}>
                          <span className="team-name">{matchup.team1?.team_name || 'Unknown Team'}</span>
                          {team1Points > team2Points && <span className="winner-badge">🏆</span>}
                        </div>
                        <div className="vs">VS</div>
                        <div className={`team-header ${team2Points > team1Points ? 'winner' : ''}`}>
                          <span className="team-name">{matchup.team2?.team_name || 'Unknown Team'}</span>
                          {team2Points > team1Points && <span className="winner-badge">🏆</span>}
                        </div>
                      </div>
                      
                      <div className="matchup-totals">
                        <div className="total-points">Total: {team1Points.toFixed(1)} pts</div>
                        <div className="total-points">Total: {team2Points.toFixed(1)} pts</div>
                      </div>

                      {/* Detailed players when expanded */}
                      {isExpanded && (
                        <div className="bench-players-section">
                          <div className="team-players">
                            <div className="players-label">Bench Players:</div>
                            <div className="players-list">
                              {team1Players.map((player, idx) => (
                                <div key={idx} className="player-row">
                                  <span className="player-icon">🏈</span>
                                  <span className="player-name">{truncateName(player.name)}</span>
                                  <span className="player-position">({player.position})</span>
                                  <span className="player-points">- {player.points.toFixed(1)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div className="team-players">
                            <div className="players-label">Bench Players:</div>
                            <div className="players-list">
                              {team2Players.map((player, idx) => (
                                <div key={idx} className="player-row">
                                  <span className="player-icon">🏈</span>
                                  <span className="player-name">{truncateName(player.name)}</span>
                                  <span className="player-position">({player.position})</span>
                                  <span className="player-points">- {player.points.toFixed(1)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Toggle text */}
                      <div className="expand-toggle">
                        <span 
                          className="toggle-text"
                          onClick={() => toggleMatchupExpansion(matchupId)}
                          style={{
                            cursor: 'pointer',
                            color: '#007bff',
                            fontSize: '0.9em',
                            textDecoration: 'underline',
                            userSelect: 'none'
                          }}
                        >
                          {isExpanded ? '▲ Hide Players' : '▼ Show Players'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};

export default MatchupsList;
