import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  ResponsiveContainer
} from 'recharts';

const AnalyticsCharts = ({ analytics }) => {
  if (!analytics || Object.keys(analytics).length === 0) {
    return (
      <div className="no-data">
        <p>No analytics data available. Make sure you have bench scoring data loaded.</p>
      </div>
    );
  }

  const { weekly_trends, team_performance, league_stats } = analytics;

  return (
    <div className="analytics-container">
      <h2>Bench Scoring Analytics</h2>
      
      {/* League Overview Stats */}
      {league_stats && (
        <div className="stats-overview">
          <div className="stat-card">
            <h3>League Average</h3>
            <div className="stat-value">{league_stats.average_weekly_points?.toFixed(1)} pts</div>
          </div>
          <div className="stat-card">
            <h3>Highest Week</h3>
            <div className="stat-value">{league_stats.highest_weekly_score?.toFixed(1)} pts</div>
          </div>
          <div className="stat-card">
            <h3>Total Weeks</h3>
            <div className="stat-value">{league_stats.total_weeks}</div>
          </div>
          <div className="stat-card">
            <h3>Active Teams</h3>
            <div className="stat-value">{league_stats.total_teams}</div>
          </div>
        </div>
      )}

      {/* Weekly Trends Chart */}
      {weekly_trends && weekly_trends.length > 0 && (
        <div className="chart-section">
          <h3>Weekly Bench Points Trends</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={weekly_trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="average_points" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="League Average"
              />
              <Line 
                type="monotone" 
                dataKey="highest_score" 
                stroke="#82ca9d" 
                strokeWidth={2}
                name="Week High"
              />
              <Line 
                type="monotone" 
                dataKey="lowest_score" 
                stroke="#ffc658" 
                strokeWidth={2}
                name="Week Low"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Team Performance Bar Chart */}
      {team_performance && team_performance.length > 0 && (
        <div className="chart-section">
          <h3>Team Performance Comparison</h3>
          <ResponsiveContainer width="100%" height={450}>
            <BarChart 
              data={team_performance.map(team => ({
                ...team,
                team_name: team.team.team_name
              }))}
              margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="team_name" 
                angle={-45}
                textAnchor="end"
                height={80}
                interval={0}
                fontSize={12}
              />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [value.toFixed(1), name]}
                labelFormatter={(label) => `Team: ${label}`}
              />
              <Legend />
              <Bar dataKey="total_points" fill="#8884d8" name="Total Points" />
              <Bar dataKey="average_points" fill="#82ca9d" name="Average Points" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

    </div>
  );
};

export default AnalyticsCharts;
