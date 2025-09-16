#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

class StaticDataBuilder {
    constructor() {
        this.dataDir = path.join(__dirname, '..', 'stats-sleeper', 'data');
        this.outputDir = path.join(__dirname, 'frontend', 'public', 'data');
        this.teams = new Map();
        this.weeklyResults = [];
        this.matchups = [];
    }

    async build() {
        console.log('🏈 Building static data for Beer League Dashboard...');
        
        // Ensure output directory exists
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }

        try {
            // Find the latest CSV files
            const latestFiles = this.findLatestFiles();
            console.log(`📁 Using files: ${latestFiles.weeklyResults}, ${latestFiles.matchups}`);

            // Process the data
            await this.processWeeklyResults(latestFiles.weeklyResults);
            await this.processMatchups(latestFiles.matchups);

            // Generate output files
            await this.generateStandings();
            await this.generateMatchupsData();
            await this.generateAnalytics();
            await this.generateTeamsData();
            await this.generateWeeklyResultsData();

            console.log('✅ Static data build complete!');
            console.log(`📊 Generated data for ${this.teams.size} teams`);
            console.log(`📈 Processed ${this.weeklyResults.length} weekly results`);
            console.log(`🥊 Processed ${this.matchups.length} matchups`);

        } catch (error) {
            console.error('❌ Error building static data:', error);
            process.exit(1);
        }
    }

    findLatestFiles() {
        const files = fs.readdirSync(this.dataDir);
        
        const weeklyResultsFiles = files
            .filter(f => f.startsWith('weekly_results_') && f.endsWith('.csv'))
            .sort()
            .reverse();
        
        const matchupsFiles = files
            .filter(f => f.startsWith('weekly_matchups_') && f.endsWith('.csv'))
            .sort()
            .reverse();

        if (weeklyResultsFiles.length === 0 || matchupsFiles.length === 0) {
            throw new Error('No CSV files found in data directory');
        }

        return {
            weeklyResults: weeklyResultsFiles[0],
            matchups: matchupsFiles[0]
        };
    }

    async processWeeklyResults(filename) {
        return new Promise((resolve, reject) => {
            const filePath = path.join(this.dataDir, filename);
            const results = [];

            fs.createReadStream(filePath)
                .pipe(csv())
                .on('data', (row) => {
                    // Store team info
                    if (!this.teams.has(parseInt(row.roster_id))) {
                        this.teams.set(parseInt(row.roster_id), {
                            roster_id: parseInt(row.roster_id),
                            team_name: row.team_name,
                            owner_id: row.owner_id
                        });
                    }

                    // Store weekly result
                    const weeklyResult = {
                        week: parseInt(row.week),
                        roster_id: parseInt(row.roster_id),
                        team_name: row.team_name,
                        total_bench_points: parseFloat(row.total_bench_points),
                        bench_player_count: parseInt(row.bench_player_count),
                        date_recorded: row.date_recorded,
                        bench_players_json: row.bench_players_detail || '[]'
                    };

                    results.push(weeklyResult);
                })
                .on('end', () => {
                    this.weeklyResults = results;
                    resolve();
                })
                .on('error', reject);
        });
    }

    async processMatchups(filename) {
        return new Promise((resolve, reject) => {
            const filePath = path.join(this.dataDir, filename);
            const results = [];

            fs.createReadStream(filePath)
                .pipe(csv())
                .on('data', (row) => {
                    const matchup = {
                        id: results.length + 1,
                        week: parseInt(row.week),
                        matchup_id: parseInt(row.matchup_id),
                        team1_roster_id: parseInt(row.team1_roster_id),
                        team1_bench_points: parseFloat(row.team1_bench_points),
                        team2_roster_id: parseInt(row.team2_roster_id),
                        team2_bench_points: parseFloat(row.team2_bench_points),
                        winner_roster_id: row.winner_roster_id ? parseInt(row.winner_roster_id) : null,
                        margin_of_victory: row.margin_of_victory ? parseFloat(row.margin_of_victory) : null,
                        date_recorded: row.date_recorded
                    };

                    results.push(matchup);
                })
                .on('end', () => {
                    this.matchups = results;
                    resolve();
                })
                .on('error', reject);
        });
    }

    async generateStandings() {
        const standings = [];
        
        for (const [rosterId, team] of this.teams) {
            const teamResults = this.weeklyResults.filter(r => r.roster_id === rosterId);
            const teamMatchups = this.matchups.filter(m => 
                m.team1_roster_id === rosterId || m.team2_roster_id === rosterId
            );

            if (teamResults.length === 0) continue;

            const totalPoints = teamResults.reduce((sum, r) => sum + r.total_bench_points, 0);
            const averagePoints = totalPoints / teamResults.length;
            const bestWeek = Math.max(...teamResults.map(r => r.total_bench_points));
            const worstWeek = Math.min(...teamResults.map(r => r.total_bench_points));

            const wins = teamMatchups.filter(m => m.winner_roster_id === rosterId).length;
            const losses = teamMatchups.length - wins;
            const winPercentage = teamMatchups.length > 0 ? wins / teamMatchups.length : 0;

            standings.push({
                team: {
                    roster_id: team.roster_id,
                    team_name: team.team_name,
                    owner_id: team.owner_id
                },
                total_points: totalPoints,
                average_points: Math.round(averagePoints * 100) / 100,
                weeks_played: teamResults.length,
                best_week: bestWeek,
                worst_week: worstWeek,
                wins: wins,
                losses: losses,
                win_percentage: Math.round(winPercentage * 1000) / 1000
            });
        }

        // Sort by total points descending
        standings.sort((a, b) => b.total_points - a.total_points);

        fs.writeFileSync(
            path.join(this.outputDir, 'standings.json'),
            JSON.stringify(standings, null, 2)
        );
    }

    async generateMatchupsData() {
        const enrichedMatchups = this.matchups.map(matchup => {
            const team1 = this.teams.get(matchup.team1_roster_id);
            const team2 = this.teams.get(matchup.team2_roster_id);
            const winner = matchup.winner_roster_id ? this.teams.get(matchup.winner_roster_id) : null;

            // Get bench players for both teams
            const team1BenchPlayers = this.getBenchPlayersForTeam(matchup.team1_roster_id, matchup.week);
            const team2BenchPlayers = this.getBenchPlayersForTeam(matchup.team2_roster_id, matchup.week);

            return {
                id: matchup.id,
                week: matchup.week,
                matchup_id: matchup.matchup_id,
                team1: {
                    roster_id: team1.roster_id,
                    team_name: team1.team_name,
                    bench_points: matchup.team1_bench_points,
                    bench_players: team1BenchPlayers
                },
                team2: {
                    roster_id: team2.roster_id,
                    team_name: team2.team_name,
                    bench_points: matchup.team2_bench_points,
                    bench_players: team2BenchPlayers
                },
                winner: winner ? {
                    roster_id: winner.roster_id,
                    team_name: winner.team_name,
                    bench_points: winner.roster_id === matchup.team1_roster_id ? 
                        matchup.team1_bench_points : matchup.team2_bench_points,
                    bench_players: winner.roster_id === matchup.team1_roster_id ? 
                        team1BenchPlayers : team2BenchPlayers
                } : null,
                margin_of_victory: matchup.margin_of_victory,
                date_recorded: matchup.date_recorded
            };
        });

        fs.writeFileSync(
            path.join(this.outputDir, 'matchups.json'),
            JSON.stringify(enrichedMatchups, null, 2)
        );
    }

    getBenchPlayersForTeam(rosterId, week) {
        const weeklyResult = this.weeklyResults.find(r => 
            r.roster_id === rosterId && r.week === week
        );
        
        if (!weeklyResult || !weeklyResult.bench_players_json) {
            return [];
        }

        try {
            const players = JSON.parse(weeklyResult.bench_players_json);
            return Array.isArray(players) ? players : [];
        } catch (e) {
            return [];
        }
    }

    async generateAnalytics() {
        const weeks = [...new Set(this.weeklyResults.map(r => r.week))].sort((a, b) => a - b);
        const totalTeams = this.teams.size;
        
        // League stats
        const allPoints = this.weeklyResults.map(r => r.total_bench_points);
        const leagueStats = {
            total_weeks: weeks.length,
            total_teams: totalTeams,
            total_matchups: this.matchups.length,
            average_weekly_points: allPoints.reduce((a, b) => a + b, 0) / allPoints.length,
            highest_weekly_score: Math.max(...allPoints),
            lowest_weekly_score: Math.min(...allPoints),
            total_points_scored: allPoints.reduce((a, b) => a + b, 0)
        };

        // Weekly trends
        const weeklyTrends = weeks.map(week => {
            const weekResults = this.weeklyResults.filter(r => r.week === week);
            const weekPoints = weekResults.map(r => r.total_bench_points);
            
            return {
                week: week,
                average_points: weekPoints.reduce((a, b) => a + b, 0) / weekPoints.length,
                highest_score: Math.max(...weekPoints),
                lowest_score: Math.min(...weekPoints),
                total_points: weekPoints.reduce((a, b) => a + b, 0),
                teams_played: weekResults.length
            };
        });

        // Team performance (use standings data)
        const standingsData = JSON.parse(fs.readFileSync(path.join(this.outputDir, 'standings.json')));

        const analytics = {
            league_stats: leagueStats,
            weekly_trends: weeklyTrends,
            team_performance: standingsData
        };

        fs.writeFileSync(
            path.join(this.outputDir, 'analytics.json'),
            JSON.stringify(analytics, null, 2)
        );
    }

    async generateTeamsData() {
        const teamsArray = Array.from(this.teams.values());
        fs.writeFileSync(
            path.join(this.outputDir, 'teams.json'),
            JSON.stringify(teamsArray, null, 2)
        );
    }

    async generateWeeklyResultsData() {
        fs.writeFileSync(
            path.join(this.outputDir, 'weekly-results.json'),
            JSON.stringify(this.weeklyResults, null, 2)
        );
    }
}

// Run the builder
if (require.main === module) {
    const builder = new StaticDataBuilder();
    builder.build();
}

module.exports = StaticDataBuilder;
