import React from 'react';

const StandingsTable = ({ standings }) => {
  if (!standings || standings.length === 0) {
    return (
      <div className="no-data">
        <p>No standings data available. Make sure you have bench scoring data loaded.</p>
      </div>
    );
  }

  return (
    <div className="standings-container">
      <h2>Bench Scoring Standings</h2>
      <div className="table-container">
        <table className="standings-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Team</th>
              <th>Total Bench Points</th>
              <th>Weeks Won</th>
              <th>Average Points</th>
              <th>Best Week</th>
              <th>Worst Week</th>
            </tr>
          </thead>
          <tbody>
            {standings.map((standing, index) => (
              <tr key={standing.team.roster_id} className={index < 3 ? `rank-${index + 1}` : ''}>
                <td className="rank-cell">
                  {index + 1}
                  {index === 0 && <span className="trophy">🏆</span>}
                  {index === 1 && <span className="trophy">🥈</span>}
                  {index === 2 && <span className="trophy">🥉</span>}
                </td>
                <td className="team-name">{standing.team.team_name}</td>
                <td className="points">{(standing.total_points || 0).toFixed(1)}</td>
                <td className="weeks-won">{standing.wins || 0}</td>
                <td className="avg-points">{(standing.average_points || 0).toFixed(1)}</td>
                <td className="best-week">{(standing.best_week || 0).toFixed(1)}</td>
                <td className="worst-week">{(standing.worst_week || 0).toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StandingsTable;
