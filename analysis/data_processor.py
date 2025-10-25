"""
Processador de dados para análise de jogos

✅ VERSÃO DEFINITIVA:
- H2H: Últimos 3 anos entre as equipas
- Forma Recente: Últimos 10 jogos NO CAMPEONATO (INCLUI H2H se houver)
- SEM FILTRAGEM de H2H na forma recente!
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from api.api_client import APIFootballClient
from config.config import ANALYSIS_PARAMS, CURRENT_SEASON

class DataProcessor:
    """Processador de dados da API para análise"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.api = APIFootballClient()
    
    def process_fixture_data(self, fixture: Dict) -> Dict:
        """
        Processar dados de um jogo da API para formato interno
        
        Args:
            fixture: Dados do jogo da API
        
        Returns:
            Dicionário com dados processados
        """
        fixture_data = fixture.get('fixture', {})
        league_data = fixture.get('league', {})
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        score = fixture.get('score', {})
        
        # Calcular golos na primeira parte
        halftime = score.get('halftime', {})
        home_ht = halftime.get('home', 0) or 0
        away_ht = halftime.get('away', 0) or 0
        total_first_half = home_ht + away_ht
        
        return {
            'id': fixture_data.get('id'),
            'league_id': league_data.get('id'),
            'season': league_data.get('season'),
            'date': fixture_data.get('date'),
            'home_team_id': teams.get('home', {}).get('id'),
            'away_team_id': teams.get('away', {}).get('id'),
            'home_team_name': teams.get('home', {}).get('name'),
            'away_team_name': teams.get('away', {}).get('name'),
            'status': fixture_data.get('status', {}).get('short'),
            'home_goals_fulltime': goals.get('home'),
            'away_goals_fulltime': goals.get('away'),
            'home_goals_halftime': home_ht,
            'away_goals_halftime': away_ht,
            'home_goals_first_half': home_ht,
            'away_goals_first_half': away_ht,
            'total_goals_first_half': total_first_half
        }
    
    def save_fixture_to_db(self, fixture: Dict):
        """
        Guardar jogo na base de dados
        
        Args:
            fixture: Dados do jogo da API
        """
        processed = self.process_fixture_data(fixture)
        
        # Guardar equipas
        teams = fixture.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        self.db.insert_team(
            home_team.get('id'),
            home_team.get('name'),
            home_team.get('logo')
        )
        
        self.db.insert_team(
            away_team.get('id'),
            away_team.get('name'),
            away_team.get('logo')
        )
        
        # Guardar liga
        league = fixture.get('league', {})
        self.db.insert_league(
            league.get('id'),
            league.get('name'),
            league.get('country'),
            league.get('season')
        )
        
        # Guardar jogo
        self.db.insert_match(processed)
    
    def calculate_team_first_half_stats(self, team_id: int, matches: List[Dict]) -> Dict:
        """
        Calcular estatísticas de golos na 1ª parte E Over 1.5 FT para uma equipa
        
        Args:
            team_id: ID da equipa
            matches: Lista de jogos
        
        Returns:
            Estatísticas calculadas
        """
        total_games = len(matches)
        
        if total_games == 0:
            return {
                'games_played': 0,
                'goals_scored_first_half': 0,
                'goals_conceded_first_half': 0,
                'games_with_first_half_goal': 0,
                'first_half_goal_percentage': 0,
                'avg_goals_first_half': 0,
                'games_over15': 0,
                'over15_percentage': 0
            }
        
        goals_scored = 0
        goals_conceded = 0
        games_with_goal = 0
        games_over15 = 0
        
        for match in matches:
            is_home = match['home_team_id'] == team_id
            
            if is_home:
                goals_scored += match.get('home_goals_first_half', 0) or 0
                goals_conceded += match.get('away_goals_first_half', 0) or 0
            else:
                goals_scored += match.get('away_goals_first_half', 0) or 0
                goals_conceded += match.get('home_goals_first_half', 0) or 0
            
            # Conta se houve golo na 1ª parte
            total_fh = match.get('total_goals_first_half', 0) or 0
            if total_fh > 0:
                games_with_goal += 1
            
            # Conta se houve Over 1.5 FT (2+ golos no jogo todo)
            home_ft = match.get('home_goals_fulltime', 0) or 0
            away_ft = match.get('away_goals_fulltime', 0) or 0
            total_ft = home_ft + away_ft
            if total_ft >= 2:
                games_over15 += 1
        
        return {
            'games_played': total_games,
            'goals_scored_first_half': goals_scored,
            'goals_conceded_first_half': goals_conceded,
            'games_with_first_half_goal': games_with_goal,
            'first_half_goal_percentage': (games_with_goal / total_games) * 100,
            'avg_goals_first_half': goals_scored / total_games,
            'avg_goals_conceded_first_half': goals_conceded / total_games,
            'games_over15': games_over15,
            'over15_percentage': (games_over15 / total_games) * 100
        }
    
    def calculate_h2h_stats(self, h2h_matches: List[Dict]) -> Dict:
        """
        Calcular estatísticas dos confrontos diretos (Over 0.5 HT e Over 1.5 FT)
        
        Args:
            h2h_matches: Lista de jogos entre as duas equipas
        
        Returns:
            Estatísticas dos confrontos diretos
        """
        total_matches = len(h2h_matches)
        
        if total_matches == 0:
            return {
                'total_matches': 0,
                'matches_with_first_half_goal': 0,
                'first_half_goal_percentage': 0,
                'avg_first_half_goals': 0,
                'total_first_half_goals': 0,
                'matches_over15': 0,
                'over15_percentage': 0
            }
        
        matches_with_goal = 0
        total_goals = 0
        matches_over15 = 0
        
        for match in h2h_matches:
            # Over 0.5 HT
            fh_goals = match.get('total_goals_first_half', 0) or 0
            total_goals += fh_goals
            
            if fh_goals > 0:
                matches_with_goal += 1
            
            # Over 1.5 FT
            home_ft = match.get('home_goals_fulltime', 0) or 0
            away_ft = match.get('away_goals_fulltime', 0) or 0
            total_ft = home_ft + away_ft
            if total_ft >= 2:
                matches_over15 += 1
        
        return {
            'total_matches': total_matches,
            'matches_with_first_half_goal': matches_with_goal,
            'first_half_goal_percentage': (matches_with_goal / total_matches) * 100,
            'avg_first_half_goals': total_goals / total_matches,
            'total_first_half_goals': total_goals,
            'matches_over15': matches_over15,
            'over15_percentage': (matches_over15 / total_matches) * 100
        }
    
    def fetch_and_save_team_history(self, team_id: int, league_id: int, 
                            num_games: int = 10) -> List[Dict]:
        """
        Buscar e guardar TODOS os jogos de uma equipa da temporada atual
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
            num_games: IGNORADO - busca todos da season atual
        
        Returns:
            Lista de jogos processados
        """
        print(f"   📥 Buscando TODOS os jogos da equipa {team_id} na temporada {CURRENT_SEASON}...")
        
        # Buscar TODOS os jogos da temporada atual
        fixtures = self.api.get_team_fixtures_by_league(
            team_id=team_id,
            league_id=league_id,
            season=CURRENT_SEASON
        )
        
        # Filtrar apenas jogos finalizados
        team_fixtures = [
            f for f in fixtures 
            if f.get('fixture', {}).get('status', {}).get('short') == 'FT'
        ]
        
        # Ordenar por data (mais recente primeiro)
        team_fixtures.sort(
            key=lambda x: x.get('fixture', {}).get('date', ''), 
            reverse=True
        )
        
        # Guardar TODOS
        saved_matches = []
        for fixture in team_fixtures:
            self.save_fixture_to_db(fixture)
            saved_matches.append(self.process_fixture_data(fixture))
        
        print(f"      ✅ Guardados {len(saved_matches)} jogos da temporada {CURRENT_SEASON}")
        return saved_matches
    
    def fetch_and_save_h2h(self, team1_id: int, team2_id: int, 
                      years: int = 3, league_id: int = None) -> List[Dict]:
        """
        Buscar e guardar confrontos diretos dos últimos X anos
        
        Args:
            team1_id: ID da primeira equipa
            team2_id: ID da segunda equipa
            years: Número de anos a analisar
            league_id: ID da liga para filtrar apenas campeonato interno
        
        Returns:
            Lista de confrontos processados
        """
        print(f"   📥 Buscando confrontos diretos dos últimos {years} anos...")
        
        fixtures = self.api.get_head_to_head(team1_id, team2_id, years=years, league_id=league_id)
        
        saved_matches = []
        for fixture in fixtures:
            if fixture.get('fixture', {}).get('status', {}).get('short') == 'FT':
                self.save_fixture_to_db(fixture)
                saved_matches.append(self.process_fixture_data(fixture))
        
        print(f"      ✅ Guardados {len(saved_matches)} confrontos diretos")
        return saved_matches
    
    def get_match_analysis_data(self, home_team_id: int, away_team_id: int, 
                               league_id: int) -> Dict:
        """
        Obter todos os dados necessários para análise de um jogo
        
        ✅ LÓGICA DEFINITIVA:
        1. H2H: Últimos 3 anos entre as equipas
        2. Forma: Últimos 10 jogos no campeonato (INCLUI H2H se houver!)
        3. SEM FILTRAGEM de H2H na forma recente
        
        Args:
            home_team_id: ID da equipa da casa
            away_team_id: ID da equipa visitante
            league_id: ID da liga
        
        Returns:
            Dicionário com todos os dados de análise
        """
        print(f"\n🔍 Recolhendo dados para análise...")
        
        # 1. Confrontos diretos - SEMPRE buscar da API (últimos 3 anos)
        print(f"   📥 Buscando confrontos diretos (últimos {ANALYSIS_PARAMS['direct_confrontations_years']} anos)...")
        self.fetch_and_save_h2h(home_team_id, away_team_id,
                            years=ANALYSIS_PARAMS['direct_confrontations_years'],
                            league_id=league_id)
        h2h_matches = self.db.get_head_to_head(home_team_id, away_team_id, limit=50)
        
        print(f"   ✅ Total: {len(h2h_matches)} confrontos diretos")
        
        # 2. Forma recente da equipa da casa - ÚLTIMOS 10 JOGOS (inclui H2H!)
        print(f"\n   📥 Buscando últimos 10 jogos da equipa da CASA...")
        self.fetch_and_save_team_history(home_team_id, league_id, 
                                        ANALYSIS_PARAMS['recent_form_games'])
        home_matches = self.db.get_team_recent_matches_by_league(
            home_team_id,
            league_id,
            10  # Últimos 10 jogos
        )
        print(f"   ✅ Equipa CASA: {len(home_matches)} jogos analisados")

        # 3. Forma recente da equipa visitante - ÚLTIMOS 10 JOGOS (inclui H2H!)
        print(f"\n   📥 Buscando últimos 10 jogos da equipa VISITANTE...")
        self.fetch_and_save_team_history(away_team_id, league_id,
                                        ANALYSIS_PARAMS['recent_form_games'])
        away_matches = self.db.get_team_recent_matches_by_league(
            away_team_id,
            league_id,
            10  # Últimos 10 jogos
        )
        print(f"   ✅ Equipa VISITANTE: {len(away_matches)} jogos analisados")
        
        # Calcular estatísticas
        h2h_stats = self.calculate_h2h_stats(h2h_matches)
        home_stats = self.calculate_team_first_half_stats(home_team_id, home_matches)
        away_stats = self.calculate_team_first_half_stats(away_team_id, away_matches)
        
        print(f"\n   📊 RESUMO:")
        print(f"      • H2H: {h2h_stats['total_matches']} jogos")
        print(f"      • Casa: {home_stats['games_played']} jogos")
        print(f"      • Visitante: {away_stats['games_played']} jogos")
        
        return {
            'h2h': {
                'matches': h2h_matches,
                'stats': h2h_stats
            },
            'home_team': {
                'matches': home_matches,
                'stats': home_stats
            },
            'away_team': {
                'matches': away_matches,
                'stats': away_stats
            }
        }
    
    def get_match_timeline_visualization(self, match: Dict) -> str:
        """
        Criar visualização dos golos por intervalos de tempo
        
        Args:
            match: Dados do jogo
        
        Returns:
            String com visualização formatada
        """
        home_team = match.get('home_team_name', 'Casa')
        away_team = match.get('away_team_name', 'Fora')
        
        home_ht = match.get('home_goals_halftime', 0) or 0
        away_ht = match.get('away_goals_halftime', 0) or 0
        home_ft = match.get('home_goals_fulltime', 0) or 0
        away_ft = match.get('away_goals_fulltime', 0) or 0
        
        # Calcular golos na 2ª parte
        home_2h = home_ft - home_ht
        away_2h = away_ft - away_ht
        
        viz = f"\n   {'='*60}\n"
        viz += f"   {home_team} vs {away_team}\n"
        viz += f"   {'='*60}\n\n"
        
        # 1ª Parte (0-45min)
        viz += f"   ⏱️  1ª PARTE (0-45')\n"
        viz += f"   🏠 {home_team}: {'⚽' * home_ht} ({home_ht})\n"
        viz += f"   ✈️  {away_team}: {'⚽' * away_ht} ({away_ht})\n"
        viz += f"   📊 Total: {home_ht + away_ht} golo(s)\n\n"
        
        # 2ª Parte (46-90min)
        viz += f"   ⏱️  2ª PARTE (46-90')\n"
        viz += f"   🏠 {home_team}: {'⚽' * home_2h} ({home_2h})\n"
        viz += f"   ✈️  {away_team}: {'⚽' * away_2h} ({away_2h})\n"
        viz += f"   📊 Total: {home_2h + away_2h} golo(s)\n\n"
        
        # Resultado Final
        viz += f"   🏁 RESULTADO FINAL: {home_ft} - {away_ft}\n"
        viz += f"   {'='*60}\n"
        
        return viz

if __name__ == "__main__":
    # Teste do processador
    processor = DataProcessor()
    print("✅ Data Processor inicializado com sucesso!")