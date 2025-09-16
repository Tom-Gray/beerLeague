from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Team(Base):
    """Team model representing fantasy football teams."""
    __tablename__ = 'teams'
    
    roster_id = Column(Integer, primary_key=True)
    owner_id = Column(String(50))
    team_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    weekly_results = relationship("WeeklyResult", back_populates="team")
    matchups_as_team1 = relationship("Matchup", foreign_keys="Matchup.team1_roster_id", back_populates="team1")
    matchups_as_team2 = relationship("Matchup", foreign_keys="Matchup.team2_roster_id", back_populates="team2")
    
    def __repr__(self):
        return f'<Team {self.team_name} (ID: {self.roster_id})>'

class WeeklyResult(Base):
    """Weekly bench scoring results for each team."""
    __tablename__ = 'weekly_results'
    
    id = Column(Integer, primary_key=True)
    week = Column(Integer, nullable=False)
    roster_id = Column(Integer, ForeignKey('teams.roster_id'), nullable=False)
    total_bench_points = Column(Float, nullable=False)
    bench_player_count = Column(Integer, nullable=False)
    date_recorded = Column(DateTime, nullable=False)
    bench_players_json = Column(Text)  # JSON string of bench player details
    
    # Relationships
    team = relationship("Team", back_populates="weekly_results")
    
    def __repr__(self):
        return f'<WeeklyResult Week {self.week}: {self.team.team_name} - {self.total_bench_points} pts>'

class Matchup(Base):
    """Head-to-head bench scoring matchups."""
    __tablename__ = 'matchups'
    
    id = Column(Integer, primary_key=True)
    week = Column(Integer, nullable=False)
    matchup_id = Column(Integer, nullable=False)
    team1_roster_id = Column(Integer, ForeignKey('teams.roster_id'), nullable=False)
    team1_bench_points = Column(Float, nullable=False)
    team2_roster_id = Column(Integer, ForeignKey('teams.roster_id'), nullable=False)
    team2_bench_points = Column(Float, nullable=False)
    winner_roster_id = Column(Integer, ForeignKey('teams.roster_id'))
    margin_of_victory = Column(Float)
    date_recorded = Column(DateTime, nullable=False)
    
    # Relationships
    team1 = relationship("Team", foreign_keys=[team1_roster_id], back_populates="matchups_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_roster_id], back_populates="matchups_as_team2")
    
    def __repr__(self):
        return f'<Matchup Week {self.week}: {self.team1.team_name} vs {self.team2.team_name}>'
