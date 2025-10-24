"""
Modelos de dados para a base de dados SQLite
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Team:
    """Modelo para equipas"""
    id: int
    name: str
    logo: str
    country: str
    
@dataclass
class League:
    """Modelo para ligas"""
    id: int
    name: str
    country: str
    season: int

@dataclass
class Match:
    """Modelo para jogos"""
    id: int
    league_id: int
    season: int
    date: datetime
    home_team_id: int
    away_team_id: int
    home_team_name: str
    away_team_name: str
    status: str  # NS (Not Started), 1H, HT, 2H, FT, etc.
    
    # Resultados
    home_goals_fulltime: Optional[int] = None
    away_goals_fulltime: Optional[int] = None
    home_goals_halftime: Optional[int] = None
    away_goals_halftime: Optional[int] = None
    
    # Estatísticas
    home_goals_first_half: Optional[int] = None
    away_goals_first_half: Optional[int] = None
    total_goals_first_half: Optional[int] = None
    
@dataclass
class MatchStatistics:
    """Estatísticas detalhadas de um jogo"""
    match_id: int
    team_id: int
    
    # Estatísticas gerais
    shots_on_goal: Optional[int] = None
    shots_off_goal: Optional[int] = None
    total_shots: Optional[int] = None
    blocked_shots: Optional[int] = None
    shots_insidebox: Optional[int] = None
    shots_outsidebox: Optional[int] = None
    fouls: Optional[int] = None
    corner_kicks: Optional[int] = None
    offsides: Optional[int] = None
    ball_possession: Optional[str] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    goalkeeper_saves: Optional[int] = None
    total_passes: Optional[int] = None
    passes_accurate: Optional[int] = None
    passes_percentage: Optional[str] = None

@dataclass
class TeamForm:
    """Forma recente de uma equipa"""
    team_id: int
    league_id: int
    season: int
    
    # Últimos 10 jogos
    games_played: int
    wins: int
    draws: int
    losses: int
    
    # Golos
    goals_scored: int
    goals_conceded: int
    goals_scored_first_half: int
    goals_conceded_first_half: int
    
    # Percentagens
    first_half_goal_percentage: float  # % de jogos com golo na 1ª parte
    avg_goals_per_game: float
    avg_goals_first_half: float
    
    # Casa vs Fora
    home_games: int
    away_games: int
    home_first_half_goals: int
    away_first_half_goals: int

@dataclass
class HeadToHead:
    """Confrontos diretos entre duas equipas"""
    team1_id: int
    team2_id: int
    league_id: int
    
    # Últimos 5 confrontos
    total_matches: int
    team1_wins: int
    team2_wins: int
    draws: int
    
    # Golos na 1ª parte nos confrontos diretos
    matches_with_first_half_goal: int
    first_half_goal_percentage: float
    avg_first_half_goals: float
    
    last_matches: list  # Lista dos últimos jogos entre as equipas

@dataclass
class DailyPrediction:
    """Previsão diária para um jogo"""
    match_id: int
    date: datetime
    league_name: str
    home_team: str
    away_team: str
    
    # Scores
    overall_score: float  # Score final (0-100)
    confidence_level: str  # HIGH, MEDIUM, LOW
    
    # Scores parciais
    h2h_score: float
    home_form_score: float
    away_form_score: float
    first_half_stats_score: float
    
    # Análise
    recommendation: str  # YES, NO, MAYBE
    reasoning: str  # Explicação da recomendação
    
    created_at: datetime = datetime.now()