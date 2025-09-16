"""
Report generation and formatting for bench scoring system.
"""
from typing import List, Dict
from datetime import datetime
from tabulate import tabulate
from jinja2 import Template
from bench_scorer import WeeklyBenchResult, BenchMatchup, SeasonBenchStandings
from bench_data_manager import BenchDataManager
from config import config

class BenchReporter:
    """Generate formatted reports and summaries."""
    
    def __init__(self, data_manager: BenchDataManager = None):
        self.data_manager = data_manager or BenchDataManager(config.data_dir)
    
    def create_weekly_report(self, week: int, results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> str:
        """Create weekly report with results and matchups."""
        if not results and not matchups:
            return f"No data available for Week {week}"
        
        report_lines = []
        report_lines.append(f"=== BEER LEAGUE BENCH SCORING - WEEK {week} ===")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Weekly Results Summary
        if results:
            report_lines.append("WEEKLY BENCH RESULTS:")
            report_lines.append("-" * 50)
            
            # Sort by total bench points (descending)
            sorted_results = sorted(results, key=lambda x: x.total_bench_points, reverse=True)
            
            table_data = []
            for rank, result in enumerate(sorted_results, 1):
                table_data.append([
                    rank,
                    result.team_name,
                    f"{result.total_bench_points:.2f}",
                    result.bench_player_count,
                    f"{result.total_bench_points / result.bench_player_count:.2f}" if result.bench_player_count > 0 else "0.00"
                ])
            
            headers = ["Rank", "Team", "Bench Points", "Players", "Avg/Player"]
            report_lines.append(tabulate(table_data, headers=headers, tablefmt="grid"))
            report_lines.append("")
        
        # Matchup Results
        if matchups:
            report_lines.append("BENCH MATCHUP RESULTS:")
            report_lines.append("-" * 50)
            
            for matchup in matchups:
                winner_name = matchup.team1_name if matchup.winner_roster_id == matchup.team1_roster_id else matchup.team2_name
                report_lines.append(f"Matchup {matchup.matchup_id}:")
                report_lines.append(f"  {matchup.team1_name}: {matchup.team1_bench_points:.2f}")
                report_lines.append(f"  {matchup.team2_name}: {matchup.team2_bench_points:.2f}")
                report_lines.append(f"  Winner: {winner_name} (Margin: {matchup.margin_of_victory:.2f})")
                report_lines.append("")
        
        # Top Bench Performers
        if results:
            report_lines.append("TOP BENCH PERFORMERS:")
            report_lines.append("-" * 50)
            
            all_bench_players = []
            for result in results:
                for player in result.bench_players:
                    all_bench_players.append((player, result.team_name))
            
            # Sort by points (descending)
            top_players = sorted(all_bench_players, key=lambda x: x[0].points, reverse=True)[:10]
            
            player_table = []
            for rank, (player, team_name) in enumerate(top_players, 1):
                player_table.append([
                    rank,
                    player.player_name,
                    player.position,
                    player.team,
                    f"{player.points:.2f}",
                    team_name
                ])
            
            player_headers = ["Rank", "Player", "Pos", "NFL Team", "Points", "Fantasy Team"]
            report_lines.append(tabulate(player_table, headers=player_headers, tablefmt="grid"))
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def create_matchup_summary(self, week: int, matchups: List[BenchMatchup]) -> str:
        """Create matchup summary for a specific week."""
        if not matchups:
            return f"No matchups found for Week {week}"
        
        summary_lines = []
        summary_lines.append(f"Week {week} Bench Matchup Summary")
        summary_lines.append("=" * 40)
        
        total_matchups = len(matchups)
        total_points = sum(m.team1_bench_points + m.team2_bench_points for m in matchups)
        avg_points_per_team = total_points / (total_matchups * 2) if total_matchups > 0 else 0
        
        summary_lines.append(f"Total Matchups: {total_matchups}")
        summary_lines.append(f"Average Bench Points per Team: {avg_points_per_team:.2f}")
        summary_lines.append("")
        
        # Closest matchups
        closest_matchups = sorted(matchups, key=lambda x: x.margin_of_victory)[:3]
        summary_lines.append("Closest Matchups:")
        for i, matchup in enumerate(closest_matchups, 1):
            winner_name = matchup.team1_name if matchup.winner_roster_id == matchup.team1_roster_id else matchup.team2_name
            summary_lines.append(f"{i}. {winner_name} wins by {matchup.margin_of_victory:.2f}")
        
        summary_lines.append("")
        
        # Biggest blowouts
        biggest_margins = sorted(matchups, key=lambda x: x.margin_of_victory, reverse=True)[:3]
        summary_lines.append("Biggest Margins:")
        for i, matchup in enumerate(biggest_margins, 1):
            winner_name = matchup.team1_name if matchup.winner_roster_id == matchup.team1_roster_id else matchup.team2_name
            summary_lines.append(f"{i}. {winner_name} wins by {matchup.margin_of_victory:.2f}")
        
        return "\n".join(summary_lines)
    
    def create_season_summary(self, standings: List[SeasonBenchStandings]) -> str:
        """Create season summary report."""
        if not standings:
            return "No season data available"
        
        report_lines = []
        report_lines.append("=== BEER LEAGUE BENCH SCORING - SEASON SUMMARY ===")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Season Standings
        report_lines.append("SEASON STANDINGS:")
        report_lines.append("-" * 80)
        
        table_data = []
        for rank, standing in enumerate(standings, 1):
            table_data.append([
                rank,
                standing.team_name,
                f"{standing.wins}-{standing.losses}",
                f"{standing.win_percentage:.3f}",
                f"{standing.total_bench_points:.2f}",
                f"{standing.average_bench_points:.2f}",
                f"{standing.best_week_points:.2f}",
                f"W{standing.best_week_number}"
            ])
        
        headers = ["Rank", "Team", "W-L", "Win%", "Total Pts", "Avg Pts", "Best Week", "Week"]
        report_lines.append(tabulate(table_data, headers=headers, tablefmt="grid"))
        report_lines.append("")
        
        # Season Statistics
        total_weeks = max(s.total_weeks for s in standings) if standings else 0
        total_points = sum(s.total_bench_points for s in standings)
        avg_points_per_week = total_points / (len(standings) * total_weeks) if standings and total_weeks > 0 else 0
        
        report_lines.append("SEASON STATISTICS:")
        report_lines.append("-" * 30)
        report_lines.append(f"Weeks Played: {total_weeks}")
        report_lines.append(f"Total Teams: {len(standings)}")
        report_lines.append(f"Total Bench Points: {total_points:.2f}")
        report_lines.append(f"Average Points per Team per Week: {avg_points_per_week:.2f}")
        report_lines.append("")
        
        # Best and Worst Performances
        if standings:
            best_week = max(standings, key=lambda x: x.best_week_points)
            worst_week = min(standings, key=lambda x: x.worst_week_points)
            
            report_lines.append("NOTABLE PERFORMANCES:")
            report_lines.append("-" * 30)
            report_lines.append(f"Best Week: {best_week.team_name} - {best_week.best_week_points:.2f} pts (Week {best_week.best_week_number})")
            report_lines.append(f"Worst Week: {worst_week.team_name} - {worst_week.worst_week_points:.2f} pts (Week {worst_week.worst_week_number})")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def create_win_loss_table(self, standings: List[SeasonBenchStandings]) -> str:
        """Create win/loss table."""
        if not standings:
            return "No standings data available"
        
        table_lines = []
        table_lines.append("WIN/LOSS RECORDS:")
        table_lines.append("-" * 40)
        
        table_data = []
        for standing in standings:
            table_data.append([
                standing.team_name,
                standing.wins,
                standing.losses,
                f"{standing.win_percentage:.3f}",
                f"{standing.total_bench_points:.2f}"
            ])
        
        headers = ["Team", "Wins", "Losses", "Win%", "Total Points"]
        table_lines.append(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        return "\n".join(table_lines)
    
    def export_html_report(self, standings: List[SeasonBenchStandings], filename: str) -> None:
        """Export HTML report for enhanced presentation."""
        if not standings:
            print("No standings data to export")
            return
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Beer League Bench Scoring - Season Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; color: #2c3e50; }
        .standings-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .standings-table th, .standings-table td { 
            border: 1px solid #ddd; padding: 8px; text-align: center; 
        }
        .standings-table th { background-color: #f2f2f2; }
        .standings-table tr:nth-child(even) { background-color: #f9f9f9; }
        .stats-section { margin: 20px 0; }
        .highlight { background-color: #e8f5e8; }
        .rank-1 { background-color: #ffd700; }
        .rank-2 { background-color: #c0c0c0; }
        .rank-3 { background-color: #cd7f32; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 Beer League Bench Scoring</h1>
        <h2>Season Summary Report</h2>
        <p>Generated: {{ timestamp }}</p>
    </div>
    
    <div class="stats-section">
        <h3>Season Standings</h3>
        <table class="standings-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th>Record</th>
                    <th>Win %</th>
                    <th>Total Points</th>
                    <th>Avg Points</th>
                    <th>Best Week</th>
                    <th>Worst Week</th>
                </tr>
            </thead>
            <tbody>
                {% for standing in standings %}
                <tr class="{% if loop.index == 1 %}rank-1{% elif loop.index == 2 %}rank-2{% elif loop.index == 3 %}rank-3{% endif %}">
                    <td>{{ loop.index }}</td>
                    <td>{{ standing.team_name }}</td>
                    <td>{{ standing.wins }}-{{ standing.losses }}</td>
                    <td>{{ "%.3f"|format(standing.win_percentage) }}</td>
                    <td>{{ "%.2f"|format(standing.total_bench_points) }}</td>
                    <td>{{ "%.2f"|format(standing.average_bench_points) }}</td>
                    <td>{{ "%.2f"|format(standing.best_week_points) }} (W{{ standing.best_week_number }})</td>
                    <td>{{ "%.2f"|format(standing.worst_week_points) }} (W{{ standing.worst_week_number }})</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="stats-section">
        <h3>Season Statistics</h3>
        <ul>
            <li><strong>Total Teams:</strong> {{ standings|length }}</li>
            <li><strong>Weeks Played:</strong> {{ max_weeks }}</li>
            <li><strong>Total Bench Points:</strong> {{ "%.2f"|format(total_points) }}</li>
            <li><strong>Average Points per Team per Week:</strong> {{ "%.2f"|format(avg_points_per_week) }}</li>
        </ul>
    </div>
    
    {% if best_performer and worst_performer %}
    <div class="stats-section">
        <h3>Notable Performances</h3>
        <ul>
            <li><strong>Best Single Week:</strong> {{ best_performer.team_name }} - {{ "%.2f"|format(best_performer.best_week_points) }} points (Week {{ best_performer.best_week_number }})</li>
            <li><strong>Worst Single Week:</strong> {{ worst_performer.team_name }} - {{ "%.2f"|format(worst_performer.worst_week_points) }} points (Week {{ worst_performer.worst_week_number }})</li>
        </ul>
    </div>
    {% endif %}
</body>
</html>
        """
        
        try:
            template = Template(html_template)
            
            # Calculate statistics
            total_points = sum(s.total_bench_points for s in standings)
            max_weeks = max(s.total_weeks for s in standings) if standings else 0
            avg_points_per_week = total_points / (len(standings) * max_weeks) if standings and max_weeks > 0 else 0
            
            best_performer = max(standings, key=lambda x: x.best_week_points) if standings else None
            worst_performer = min(standings, key=lambda x: x.worst_week_points) if standings else None
            
            html_content = template.render(
                standings=standings,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_points=total_points,
                max_weeks=max_weeks,
                avg_points_per_week=avg_points_per_week,
                best_performer=best_performer,
                worst_performer=worst_performer
            )
            
            filepath = self.data_manager.get_file_path(filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Exported HTML report to {filepath}")
            
        except Exception as e:
            print(f"Error exporting HTML report: {e}")
    
    def create_team_detail_report(self, team_standing: SeasonBenchStandings) -> str:
        """Create detailed report for a specific team."""
        report_lines = []
        report_lines.append(f"=== TEAM DETAIL REPORT: {team_standing.team_name} ===")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Team Summary
        report_lines.append("TEAM SUMMARY:")
        report_lines.append("-" * 30)
        report_lines.append(f"Record: {team_standing.wins}-{team_standing.losses} ({team_standing.win_percentage:.3f})")
        report_lines.append(f"Total Bench Points: {team_standing.total_bench_points:.2f}")
        report_lines.append(f"Average Points per Week: {team_standing.average_bench_points:.2f}")
        report_lines.append(f"Best Week: {team_standing.best_week_points:.2f} (Week {team_standing.best_week_number})")
        report_lines.append(f"Worst Week: {team_standing.worst_week_points:.2f} (Week {team_standing.worst_week_number})")
        report_lines.append("")
        
        # Weekly Performance
        if team_standing.weekly_results:
            report_lines.append("WEEKLY PERFORMANCE:")
            report_lines.append("-" * 30)
            
            weekly_table = []
            for result in sorted(team_standing.weekly_results, key=lambda x: x.week):
                weekly_table.append([
                    result.week,
                    f"{result.total_bench_points:.2f}",
                    result.bench_player_count,
                    f"{result.total_bench_points / result.bench_player_count:.2f}" if result.bench_player_count > 0 else "0.00"
                ])
            
            headers = ["Week", "Points", "Players", "Avg/Player"]
            report_lines.append(tabulate(weekly_table, headers=headers, tablefmt="grid"))
            report_lines.append("")
        
        return "\n".join(report_lines)

# Convenience functions
def create_weekly_report(week: int, results: List[WeeklyBenchResult], matchups: List[BenchMatchup]) -> str:
    """Create weekly report."""
    reporter = BenchReporter()
    return reporter.create_weekly_report(week, results, matchups)

def create_season_summary(standings: List[SeasonBenchStandings]) -> str:
    """Create season summary report."""
    reporter = BenchReporter()
    return reporter.create_season_summary(standings)

def export_html_report(standings: List[SeasonBenchStandings], filename: str) -> None:
    """Export HTML report."""
    reporter = BenchReporter()
    reporter.export_html_report(standings, filename)
