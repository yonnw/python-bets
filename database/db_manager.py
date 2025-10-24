"""
Gestor da base de dados SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DATABASE_PATH

class DatabaseManager:
    """Gestor da base de dados"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões à BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """Criar tabelas se não existirem"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de equipas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    logo TEXT,
                    country TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de ligas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leagues (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    country TEXT,
                    season INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id, season)
                )
            """)
            
            # Tabela de jogos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY,
                    league_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    date TIMESTAMP NOT NULL,
                    home_team_id INTEGER NOT NULL,
                    away_team_id INTEGER NOT NULL,
                    home_team_name TEXT NOT NULL,
                    away_team_name TEXT NOT NULL,
                    status TEXT,
                    home_goals_fulltime INTEGER,
                    away_goals_fulltime INTEGER,
                    home_goals_halftime INTEGER,
                    away_goals_halftime INTEGER,
                    home_goals_first_half INTEGER,
                    away_goals_first_half INTEGER,
                    total_goals_first_half INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (league_id) REFERENCES leagues (id),
                    FOREIGN KEY (home_team_id) REFERENCES teams (id),
                    FOREIGN KEY (away_team_id) REFERENCES teams (id)
                )
            """)
            
            # Tabela de estatísticas dos jogos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    shots_on_goal INTEGER,
                    shots_off_goal INTEGER,
                    total_shots INTEGER,
                    blocked_shots INTEGER,
                    shots_insidebox INTEGER,
                    shots_outsidebox INTEGER,
                    fouls INTEGER,
                    corner_kicks INTEGER,
                    offsides INTEGER,
                    ball_possession TEXT,
                    yellow_cards INTEGER,
                    red_cards INTEGER,
                    goalkeeper_saves INTEGER,
                    total_passes INTEGER,
                    passes_accurate INTEGER,
                    passes_percentage TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id),
                    FOREIGN KEY (team_id) REFERENCES teams (id),
                    UNIQUE(match_id, team_id)
                )
            """)
            
            # Tabela de previsões diárias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    date TIMESTAMP NOT NULL,
                    league_name TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    confidence_level TEXT NOT NULL,
                    h2h_score REAL,
                    home_form_score REAL,
                    away_form_score REAL,
                    first_half_stats_score REAL,
                    recommendation TEXT NOT NULL,
                    reasoning TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            """)
            
            # Índices para melhor performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_date 
                ON matches(date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_teams 
                ON matches(home_team_id, away_team_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_league_season 
                ON matches(league_id, season)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_date 
                ON daily_predictions(date)
            """)
            
            print("✅ Base de dados inicializada com sucesso!")
    
    def insert_team(self, team_id: int, name: str, logo: str = None, country: str = None):
        """Inserir ou atualizar equipa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO teams (id, name, logo, country)
                VALUES (?, ?, ?, ?)
            """, (team_id, name, logo, country))
    
    def insert_league(self, league_id: int, name: str, country: str, season: int):
        """Inserir ou atualizar liga"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO leagues (id, name, country, season)
                VALUES (?, ?, ?, ?)
            """, (league_id, name, country, season))
    
    def insert_match(self, match_data: Dict[str, Any]):
        """Inserir ou atualizar jogo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO matches (
                    id, league_id, season, date, home_team_id, away_team_id,
                    home_team_name, away_team_name, status,
                    home_goals_fulltime, away_goals_fulltime,
                    home_goals_halftime, away_goals_halftime,
                    home_goals_first_half, away_goals_first_half,
                    total_goals_first_half, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                match_data.get('id'),
                match_data.get('league_id'),
                match_data.get('season'),
                match_data.get('date'),
                match_data.get('home_team_id'),
                match_data.get('away_team_id'),
                match_data.get('home_team_name'),
                match_data.get('away_team_name'),
                match_data.get('status'),
                match_data.get('home_goals_fulltime'),
                match_data.get('away_goals_fulltime'),
                match_data.get('home_goals_halftime'),
                match_data.get('away_goals_halftime'),
                match_data.get('home_goals_first_half'),
                match_data.get('away_goals_first_half'),
                match_data.get('total_goals_first_half')
            ))
    
    def insert_prediction(self, prediction_data: Dict[str, Any]):
        """Inserir previsão diária"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO daily_predictions (
                    match_id, date, league_name, home_team, away_team,
                    overall_score, confidence_level, h2h_score, home_form_score,
                    away_form_score, first_half_stats_score, recommendation, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction_data.get('match_id'),
                prediction_data.get('date'),
                prediction_data.get('league_name'),
                prediction_data.get('home_team'),
                prediction_data.get('away_team'),
                prediction_data.get('overall_score'),
                prediction_data.get('confidence_level'),
                prediction_data.get('h2h_score'),
                prediction_data.get('home_form_score'),
                prediction_data.get('away_form_score'),
                prediction_data.get('first_half_stats_score'),
                prediction_data.get('recommendation'),
                prediction_data.get('reasoning')
            ))
    
    def get_team_recent_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """Obter últimos jogos de uma equipa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM matches
                WHERE (home_team_id = ? OR away_team_id = ?)
                AND status = 'FT'
                ORDER BY date DESC
                LIMIT ?
            """, (team_id, team_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        
    def get_team_recent_matches_by_league(self, team_id: int, league_id: int, limit: int = 10) -> List[Dict]:
        """
        Obter últimos jogos de uma equipa numa liga específica
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga para filtrar
            limit: Número de jogos a retornar
        
        Returns:
            Lista de jogos da equipa na liga
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM matches
                WHERE (home_team_id = ? OR away_team_id = ?)
                AND league_id = ?
                AND status = 'FT'
                ORDER BY date DESC
                LIMIT ?
            """, (team_id, team_id, league_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_head_to_head(self, team1_id: int, team2_id: int, limit: int = 50) -> List[Dict]:
        """Obter confrontos diretos entre duas equipas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM matches
                WHERE ((home_team_id = ? AND away_team_id = ?)
                   OR (home_team_id = ? AND away_team_id = ?))
                AND status = 'FT'
                ORDER BY date DESC
                LIMIT ?
            """, (team1_id, team2_id, team2_id, team1_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_today_matches(self) -> List[Dict]:
        """Obter jogos de hoje"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT * FROM matches
                WHERE date(date) = date(?)
                AND status = 'NS'
                ORDER BY date
            """, (today,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_today_predictions(self) -> List[Dict]:
        """Obter previsões de hoje ordenadas por score"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT * FROM daily_predictions
                WHERE date(date) = date(?)
                ORDER BY overall_score DESC
            """, (today,))
            return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    # Teste da base de dados
    db = DatabaseManager()
    print("Base de dados testada com sucesso!")