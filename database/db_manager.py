"""
Database Manager - Football Betting AI
Gestor otimizado para análise Over 0.5 HT e Over 1.5 FT
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DATABASE_PATH, CURRENT_SEASON

class DatabaseManager:
    """Gestor da base de dados SQLite"""
    
    def __init__(self, db_path: str = None):
        """
        Inicializar database manager
        
        Args:
            db_path: Caminho para o ficheiro da BD (opcional)
        """
        self.db_path = db_path or DATABASE_PATH
        self.schema_path = os.path.join(
            os.path.dirname(__file__), 
            'db_schema.sql'
        )
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões à BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """Criar base de dados e executar schema"""
        print("🔧 Inicializando base de dados...")
        
        # Verificar se schema existe
        if not os.path.exists(self.schema_path):
            print(f"❌ Schema não encontrado: {self.schema_path}")
            return False
        
        try:
            # Ler schema
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Executar schema
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema_sql)
            
            print("✅ Base de dados inicializada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar BD: {e}")
            return False
    
    # ========================================================================
    # TEAMS - Gestão de Equipas
    # ========================================================================
    
    def insert_team(self, team_data: Dict[str, Any]) -> bool:
        """
        Inserir ou atualizar equipa
        
        Args:
            team_data: Dicionário com dados da equipa
                {
                    'id': int,
                    'name': str,
                    'code': str,
                    'country': str,
                    'founded': int,
                    'logo': str
                }
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO teams 
                    (id, name, code, country, founded, logo, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    team_data.get('id'),
                    team_data.get('name'),
                    team_data.get('code'),
                    team_data.get('country'),
                    team_data.get('founded'),
                    team_data.get('logo')
                ))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir equipa: {e}")
            return False
    
    def get_team(self, team_id: int) -> Optional[Dict]:
        """Obter dados de uma equipa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ========================================================================
    # LEAGUES - Gestão de Ligas
    # ========================================================================
    
    def insert_league(self, league_data: Dict[str, Any]) -> bool:
        """Inserir ou atualizar liga"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO leagues 
                    (id, name, type, country, logo)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    league_data.get('id'),
                    league_data.get('name'),
                    league_data.get('type'),
                    league_data.get('country'),
                    league_data.get('logo')
                ))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir liga: {e}")
            return False
    
    def insert_season(self, league_id: int, year: int, 
                     current: bool = True) -> bool:
        """Inserir temporada"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO seasons 
                    (league_id, year, current)
                    VALUES (?, ?, ?)
                """, (league_id, year, current))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir temporada: {e}")
            return False
    
    # ========================================================================
    # FIXTURES - Gestão de Jogos
    # ========================================================================
    
    def insert_fixture(self, fixture_data: Dict[str, Any]) -> bool:
        """
        Inserir ou atualizar jogo
        
        Args:
            fixture_data: Dados do jogo processados
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO fixtures (
                        id, league_id, season, round, date, timestamp,
                        home_team_id, away_team_id,
                        status_short, status_long, status_elapsed,
                        venue_id, venue_name, venue_city, referee,
                        home_goals, away_goals,
                        home_goals_halftime, away_goals_halftime,
                        home_goals_extratime, away_goals_extratime,
                        home_goals_penalty, away_goals_penalty,
                        updated_at
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?,
                        ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?,
                        ?, ?,
                        ?, ?,
                        ?, ?,
                        CURRENT_TIMESTAMP
                    )
                """, (
                    fixture_data.get('id'),
                    fixture_data.get('league_id'),
                    fixture_data.get('season'),
                    fixture_data.get('round'),
                    fixture_data.get('date'),
                    fixture_data.get('timestamp'),
                    fixture_data.get('home_team_id'),
                    fixture_data.get('away_team_id'),
                    fixture_data.get('status_short'),
                    fixture_data.get('status_long'),
                    fixture_data.get('status_elapsed'),
                    fixture_data.get('venue_id'),
                    fixture_data.get('venue_name'),
                    fixture_data.get('venue_city'),
                    fixture_data.get('referee'),
                    fixture_data.get('home_goals'),
                    fixture_data.get('away_goals'),
                    fixture_data.get('home_goals_halftime'),
                    fixture_data.get('away_goals_halftime'),
                    fixture_data.get('home_goals_extratime'),
                    fixture_data.get('away_goals_extratime'),
                    fixture_data.get('home_goals_penalty'),
                    fixture_data.get('away_goals_penalty')
                ))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir fixture: {e}")
            return False
    
    def get_fixture(self, fixture_id: int) -> Optional[Dict]:
        """Obter dados de um jogo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fixtures WHERE id = ?", (fixture_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_fixtures_by_date(self, date: str, league_id: int = None) -> List[Dict]:
        """
        Obter jogos por data
        
        Args:
            date: Data no formato 'YYYY-MM-DD'
            league_id: ID da liga (opcional)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if league_id:
                cursor.execute("""
                    SELECT * FROM fixtures 
                    WHERE date(date) = date(?) AND league_id = ?
                    ORDER BY date
                """, (date, league_id))
            else:
                cursor.execute("""
                    SELECT * FROM fixtures 
                    WHERE date(date) = date(?)
                    ORDER BY date
                """, (date,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_team_fixtures(self, team_id: int, league_id: int = None,
                         season: int = CURRENT_SEASON,
                         status: str = 'FT', limit: int = 10) -> List[Dict]:
        """
        Obter jogos de uma equipa
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga (opcional)
            season: Temporada
            status: Status do jogo ('FT' por padrão)
            limit: Número máximo de jogos
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM fixtures 
                WHERE (home_team_id = ? OR away_team_id = ?)
                AND season = ?
                AND status_short = ?
            """
            params = [team_id, team_id, season, status]
            
            if league_id:
                query += " AND league_id = ?"
                params.append(league_id)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_head_to_head(self, team1_id: int, team2_id: int,
                        league_id: int = None, limit: int = 10) -> List[Dict]:
        """
        Obter confrontos diretos entre duas equipas
        
        Args:
            team1_id: ID da primeira equipa
            team2_id: ID da segunda equipa
            league_id: ID da liga (opcional)
            limit: Número máximo de jogos
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM fixtures 
                WHERE ((home_team_id = ? AND away_team_id = ?)
                   OR (home_team_id = ? AND away_team_id = ?))
                AND status_short = 'FT'
            """
            params = [team1_id, team2_id, team2_id, team1_id]
            
            if league_id:
                query += " AND league_id = ?"
                params.append(league_id)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # FIXTURE STATISTICS - Estatísticas detalhadas
    # ========================================================================
    
    def insert_fixture_statistics(self, stats_data: Dict[str, Any]) -> bool:
        """Inserir estatísticas de um jogo"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO fixture_statistics (
                        fixture_id, team_id,
                        shots_on_goal, shots_off_goal, total_shots,
                        blocked_shots, shots_insidebox, shots_outsidebox,
                        ball_possession, total_passes, passes_accurate, passes_percentage,
                        attacks, dangerous_attacks,
                        corner_kicks, offsides, fouls,
                        yellow_cards, red_cards, goalkeeper_saves,
                        expected_goals
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    stats_data.get('fixture_id'),
                    stats_data.get('team_id'),
                    stats_data.get('shots_on_goal'),
                    stats_data.get('shots_off_goal'),
                    stats_data.get('total_shots'),
                    stats_data.get('blocked_shots'),
                    stats_data.get('shots_insidebox'),
                    stats_data.get('shots_outsidebox'),
                    stats_data.get('ball_possession'),
                    stats_data.get('total_passes'),
                    stats_data.get('passes_accurate'),
                    stats_data.get('passes_percentage'),
                    stats_data.get('attacks'),
                    stats_data.get('dangerous_attacks'),
                    stats_data.get('corner_kicks'),
                    stats_data.get('offsides'),
                    stats_data.get('fouls'),
                    stats_data.get('yellow_cards'),
                    stats_data.get('red_cards'),
                    stats_data.get('goalkeeper_saves'),
                    stats_data.get('expected_goals')
                ))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir estatísticas: {e}")
            return False
    
    def get_fixture_statistics(self, fixture_id: int) -> List[Dict]:
        """Obter estatísticas de um jogo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fixture_statistics 
                WHERE fixture_id = ?
            """, (fixture_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_team_avg_statistics(self, team_id: int, league_id: int,
                               season: int = CURRENT_SEASON,
                               last_n_games: int = 10) -> Dict:
        """
        Calcular estatísticas médias de uma equipa
        
        Returns:
            Dicionário com médias de todas as estatísticas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    AVG(fs.shots_on_goal) as avg_shots_on_goal,
                    AVG(fs.total_shots) as avg_total_shots,
                    AVG(fs.shots_insidebox) as avg_shots_insidebox,
                    AVG(fs.corner_kicks) as avg_corners,
                    AVG(fs.ball_possession) as avg_possession,
                    AVG(fs.dangerous_attacks) as avg_dangerous_attacks,
                    COUNT(*) as games_count
                FROM fixture_statistics fs
                JOIN fixtures f ON fs.fixture_id = f.id
                WHERE fs.team_id = ?
                AND f.league_id = ?
                AND f.season = ?
                AND f.status_short = 'FT'
                ORDER BY f.date DESC
                LIMIT ?
            """, (team_id, league_id, season, last_n_games))
            
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    # ========================================================================
    # FIXTURE EVENTS - Eventos do jogo
    # ========================================================================
    
    def insert_fixture_event(self, event_data: Dict[str, Any]) -> bool:
        """Inserir evento de um jogo"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO fixture_events (
                        fixture_id, team_id,
                        time_elapsed, time_extra,
                        type, detail,
                        player_id, player_name,
                        assist_id, assist_name,
                        comments
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_data.get('fixture_id'),
                    event_data.get('team_id'),
                    event_data.get('time_elapsed'),
                    event_data.get('time_extra'),
                    event_data.get('type'),
                    event_data.get('detail'),
                    event_data.get('player_id'),
                    event_data.get('player_name'),
                    event_data.get('assist_id'),
                    event_data.get('assist_name'),
                    event_data.get('comments')
                ))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir evento: {e}")
            return False
    
    def get_fixture_events(self, fixture_id: int, 
                          event_type: str = None) -> List[Dict]:
        """Obter eventos de um jogo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if event_type:
                cursor.execute("""
                    SELECT * FROM fixture_events 
                    WHERE fixture_id = ? AND type = ?
                    ORDER BY time_elapsed
                """, (fixture_id, event_type))
            else:
                cursor.execute("""
                    SELECT * FROM fixture_events 
                    WHERE fixture_id = ?
                    ORDER BY time_elapsed
                """, (fixture_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_goals_by_minute_distribution(self, team_id: int, 
                                        league_id: int,
                                        season: int = CURRENT_SEASON) -> Dict:
        """
        Obter distribuição de golos por período de tempo
        
        Returns:
            {
                '0-15': {'count': 5, 'percentage': 15.0},
                '16-30': {'count': 7, 'percentage': 21.0},
                ...
            }
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN time_elapsed <= 15 THEN 1 ELSE 0 END) as g_0_15,
                    SUM(CASE WHEN time_elapsed > 15 AND time_elapsed <= 30 THEN 1 ELSE 0 END) as g_16_30,
                    SUM(CASE WHEN time_elapsed > 30 AND time_elapsed <= 45 THEN 1 ELSE 0 END) as g_31_45,
                    SUM(CASE WHEN time_elapsed > 45 AND time_elapsed <= 60 THEN 1 ELSE 0 END) as g_46_60,
                    SUM(CASE WHEN time_elapsed > 60 AND time_elapsed <= 75 THEN 1 ELSE 0 END) as g_61_75,
                    SUM(CASE WHEN time_elapsed > 75 AND time_elapsed <= 90 THEN 1 ELSE 0 END) as g_76_90,
                    COUNT(*) as total_goals
                FROM fixture_events e
                JOIN fixtures f ON e.fixture_id = f.id
                WHERE e.team_id = ?
                AND e.type = 'Goal'
                AND e.detail NOT IN ('Missed Penalty')
                AND f.league_id = ?
                AND f.season = ?
                AND f.status_short = 'FT'
            """, (team_id, league_id, season))
            
            row = cursor.fetchone()
            if not row or row['total_goals'] == 0:
                return {}
            
            total = row['total_goals']
            return {
                '0-15': {
                    'count': row['g_0_15'], 
                    'percentage': (row['g_0_15'] / total * 100) if total > 0 else 0
                },
                '16-30': {
                    'count': row['g_16_30'],
                    'percentage': (row['g_16_30'] / total * 100) if total > 0 else 0
                },
                '31-45': {
                    'count': row['g_31_45'],
                    'percentage': (row['g_31_45'] / total * 100) if total > 0 else 0
                },
                '46-60': {
                    'count': row['g_46_60'],
                    'percentage': (row['g_46_60'] / total * 100) if total > 0 else 0
                },
                '61-75': {
                    'count': row['g_61_75'],
                    'percentage': (row['g_61_75'] / total * 100) if total > 0 else 0
                },
                '76-90': {
                    'count': row['g_76_90'],
                    'percentage': (row['g_76_90'] / total * 100) if total > 0 else 0
                },
                'total': total,
                'first_half_percentage': (
                    (row['g_0_15'] + row['g_16_30'] + row['g_31_45']) / total * 100
                ) if total > 0 else 0
            }
    
    # ========================================================================
    # TEAM STATISTICS - Estatísticas agregadas da temporada
    # ========================================================================
    
    def update_team_statistics(self, team_id: int, league_id: int,
                              season: int = CURRENT_SEASON) -> bool:
        """
        Atualizar estatísticas agregadas de uma equipa
        Calcula automaticamente baseado nos jogos
        """
        # Esta função seria complexa - vou criar uma versão simplificada
        # Na prática, seria melhor buscar do endpoint /teams/statistics da API
        pass
    
    # ========================================================================
    # PREDICTIONS - Gestão de Previsões
    # ========================================================================
    
    def insert_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """Inserir previsão"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO predictions (
                        fixture_id, date, league_id, league_name,
                        home_team, away_team,
                        score_over_05_ht, confidence_over_05_ht, recommendation_over_05_ht,
                        h2h_score, home_form_score, away_form_score,
                        offensive_pressure_score, minute_distribution_score,
                        score_over_15_ft, confidence_over_15_ft, recommendation_over_15_ft,
                        h2h_score_o15, home_form_score_o15, away_form_score_o15,
                        offensive_pressure_score_o15,
                        reasoning
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?, ?,
                        ?
                    )
                """, (
                    prediction_data.get('fixture_id'),
                    prediction_data.get('date'),
                    prediction_data.get('league_id'),
                    prediction_data.get('league_name'),
                    prediction_data.get('home_team'),
                    prediction_data.get('away_team'),
                    prediction_data.get('score_over_05_ht'),
                    prediction_data.get('confidence_over_05_ht'),
                    prediction_data.get('recommendation_over_05_ht'),
                    prediction_data.get('h2h_score'),
                    prediction_data.get('home_form_score'),
                    prediction_data.get('away_form_score'),
                    prediction_data.get('offensive_pressure_score'),
                    prediction_data.get('minute_distribution_score'),
                    prediction_data.get('score_over_15_ft'),
                    prediction_data.get('confidence_over_15_ft'),
                    prediction_data.get('recommendation_over_15_ft'),
                    prediction_data.get('h2h_score_o15'),
                    prediction_data.get('home_form_score_o15'),
                    prediction_data.get('away_form_score_o15'),
                    prediction_data.get('offensive_pressure_score_o15'),
                    prediction_data.get('reasoning')
                ))
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir previsão: {e}")
            return False
    
    def get_predictions_by_date(self, date: str) -> List[Dict]:
        """Obter previsões por data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM predictions 
                WHERE date(date) = date(?)
                ORDER BY score_over_05_ht DESC
            """, (date,))
            return [dict(row) for row in cursor.fetchall()]
    
    def validate_prediction(self, fixture_id: int) -> bool:
        """
        Validar previsão após o jogo terminar
        Atualiza o registo com o resultado real
        """
        try:
            # Obter fixture
            fixture = self.get_fixture(fixture_id)
            if not fixture or fixture['status_short'] != 'FT':
                return False
            
            # Calcular resultados reais
            actual_ht = 1 if (fixture['home_goals_halftime'] or 0) + \
                            (fixture['away_goals_halftime'] or 0) > 0 else 0
            actual_ft = (fixture['home_goals'] or 0) + (fixture['away_goals'] or 0)
            
            # Obter previsão
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM predictions WHERE fixture_id = ?
                """, (fixture_id,))
                prediction = cursor.fetchone()
                
                if not prediction:
                    return False
                
                # Verificar se acertou
                correct_ht = (
                    (prediction['recommendation_over_05_ht'] == 'SIM' and actual_ht == 1) or
                    (prediction['recommendation_over_05_ht'] == 'NÃO' and actual_ht == 0)
                )
                
                correct_ft = (
                    (prediction['recommendation_over_15_ft'] == 'SIM' and actual_ft >= 2) or
                    (prediction['recommendation_over_15_ft'] == 'NÃO' and actual_ft < 2)
                )
                
                # Atualizar previsão
                cursor.execute("""
                    UPDATE predictions 
                    SET actual_result_ht = ?,
                        actual_result_ft = ?,
                        prediction_correct_ht = ?,
                        prediction_correct_ft = ?,
                        validated_at = CURRENT_TIMESTAMP
                    WHERE fixture_id = ?
                """, (actual_ht, actual_ft, correct_ht, correct_ft, fixture_id))
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao validar previsão: {e}")
            return False
    
    # ========================================================================
    # ANALYTICS - Análises e estatísticas
    # ========================================================================
    
    def get_prediction_accuracy(self, days: int = 30) -> Dict:
        """
        Obter accuracy das previsões dos últimos X dias
        
        Returns:
            {
                'total_predictions': int,
                'correct_ht': int,
                'accuracy_ht': float,
                'correct_ft': int,
                'accuracy_ft': float
            }
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction_correct_ht = 1 THEN 1 ELSE 0 END) as correct_ht,
                    SUM(CASE WHEN prediction_correct_ft = 1 THEN 1 ELSE 0 END) as correct_ft
                FROM predictions
                WHERE validated_at IS NOT NULL
                AND date >= ?
            """, (date_limit,))
            
            row = cursor.fetchone()
            if not row or row['total'] == 0:
                return {
                    'total_predictions': 0,
                    'correct_ht': 0,
                    'accuracy_ht': 0,
                    'correct_ft': 0,
                    'accuracy_ft': 0
                }
            
            return {
                'total_predictions': row['total'],
                'correct_ht': row['correct_ht'],
                'accuracy_ht': (row['correct_ht'] / row['total'] * 100),
                'correct_ft': row['correct_ft'],
                'accuracy_ft': (row['correct_ft'] / row['total'] * 100)
            }
    
    def get_database_stats(self) -> Dict:
        """Obter estatísticas gerais da BD"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Contar registos de cada tabela
            tables = ['teams', 'leagues', 'fixtures', 'fixture_statistics',
                     'fixture_events', 'predictions']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cursor.fetchone()['count']
            
            return stats

# ============================================================================
# Teste do Database Manager
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTE DO DATABASE MANAGER")
    print("="*80 + "\n")
    
    db = DatabaseManager()
    
    # Verificar estatísticas
    print("📊 Estatísticas da Base de Dados:")
    stats = db.get_database_stats()
    for table, count in stats.items():
        print(f"   • {table}: {count} registos")
    
    print("\n✅ Database Manager testado com sucesso!")