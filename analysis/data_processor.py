"""
Data Processor - Football Betting AI
Processador de dados: API → Base de Dados
Calcula métricas avançadas para análise Over 0.5 HT e Over 1.5 FT
"""

from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from api.api_client import APIFootballClient
from config.config import CURRENT_SEASON, ANALYSIS_PARAMS

class DataProcessor:
    """Processador de dados da API para análise"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.api = APIFootballClient()
        print("✅ Data Processor inicializado")
    
    # ========================================================================
    # PROCESSAMENTO DE FIXTURES
    # ========================================================================
    
    def process_fixture_from_api(self, fixture_raw: Dict) -> Dict:
        """
        Processar fixture da API para formato da BD
        
        Args:
            fixture_raw: Dados brutos da API
        
        Returns:
            Dicionário formatado para a BD
        """
        fixture_info = fixture_raw.get('fixture', {})
        league_info = fixture_raw.get('league', {})
        teams_info = fixture_raw.get('teams', {})
        goals_info = fixture_raw.get('goals', {})
        score_info = fixture_raw.get('score', {})
        
        # Processar resultados
        halftime = score_info.get('halftime', {})
        extratime = score_info.get('extratime', {})
        penalty = score_info.get('penalty', {})
        
        return {
            'id': fixture_info.get('id'),
            'league_id': league_info.get('id'),
            'season': league_info.get('season'),
            'round': league_info.get('round'),
            'date': fixture_info.get('date'),
            'timestamp': fixture_info.get('timestamp'),
            
            # Equipas
            'home_team_id': teams_info.get('home', {}).get('id'),
            'away_team_id': teams_info.get('away', {}).get('id'),
            
            # Status
            'status_short': fixture_info.get('status', {}).get('short'),
            'status_long': fixture_info.get('status', {}).get('long'),
            'status_elapsed': fixture_info.get('status', {}).get('elapsed'),
            
            # Venue
            'venue_id': fixture_info.get('venue', {}).get('id'),
            'venue_name': fixture_info.get('venue', {}).get('name'),
            'venue_city': fixture_info.get('venue', {}).get('city'),
            'referee': fixture_info.get('referee'),
            
            # Resultados
            'home_goals': goals_info.get('home'),
            'away_goals': goals_info.get('away'),
            'home_goals_halftime': halftime.get('home'),
            'away_goals_halftime': halftime.get('away'),
            'home_goals_extratime': extratime.get('home'),
            'away_goals_extratime': extratime.get('away'),
            'home_goals_penalty': penalty.get('home'),
            'away_goals_penalty': penalty.get('away'),
        }
    
    def save_fixture_complete(self, fixture_raw: Dict) -> bool:
        """
        Guardar fixture completo: jogo + equipas + liga
        
        Args:
            fixture_raw: Dados brutos da API
        
        Returns:
            True se guardou com sucesso
        """
        try:
            # 1. Guardar equipas
            teams_info = fixture_raw.get('teams', {})
            
            home_team = {
                'id': teams_info.get('home', {}).get('id'),
                'name': teams_info.get('home', {}).get('name'),
                'logo': teams_info.get('home', {}).get('logo'),
            }
            
            away_team = {
                'id': teams_info.get('away', {}).get('id'),
                'name': teams_info.get('away', {}).get('name'),
                'logo': teams_info.get('away', {}).get('logo'),
            }
            
            self.db.insert_team(home_team)
            self.db.insert_team(away_team)
            
            # 2. Guardar liga
            league_info = fixture_raw.get('league', {})
            league_data = {
                'id': league_info.get('id'),
                'name': league_info.get('name'),
                'type': league_info.get('type'),
                'country': league_info.get('country'),
                'logo': league_info.get('logo'),
            }
            self.db.insert_league(league_data)
            
            # 3. Guardar season
            self.db.insert_season(
                league_info.get('id'),
                league_info.get('season'),
                current=True
            )
            
            # 4. Guardar fixture
            fixture_data = self.process_fixture_from_api(fixture_raw)
            self.db.insert_fixture(fixture_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao guardar fixture: {e}")
            return False
    
    # ========================================================================
    # PROCESSAMENTO DE ESTATÍSTICAS
    # ========================================================================
    
    def process_fixture_statistics(self, fixture_id: int) -> bool:
        """
        Buscar e guardar estatísticas detalhadas do jogo
        
        Args:
            fixture_id: ID do jogo
        
        Returns:
            True se guardou com sucesso
        """
        try:
            print(f"   📊 Buscando estatísticas do jogo {fixture_id}...")
            
            # Buscar da API
            stats_raw = self.api.get_fixture_statistics(fixture_id)
            
            if not stats_raw:
                print(f"      ⚠️  Sem estatísticas disponíveis")
                return False
            
            # Processar estatísticas de cada equipa
            for team_stats in stats_raw:
                team_id = team_stats.get('team', {}).get('id')
                statistics = team_stats.get('statistics', [])
                
                # Converter lista de stats para dict
                stats_dict = {}
                for stat in statistics:
                    type_name = stat.get('type', '')
                    value = stat.get('value')
                    
                    # Mapear nomes da API para nomes da BD
                    mapping = {
                        'Shots on Goal': 'shots_on_goal',
                        'Shots off Goal': 'shots_off_goal',
                        'Total Shots': 'total_shots',
                        'Blocked Shots': 'blocked_shots',
                        'Shots insidebox': 'shots_insidebox',
                        'Shots outsidebox': 'shots_outsidebox',
                        'Ball Possession': 'ball_possession',
                        'Total passes': 'total_passes',
                        'Passes accurate': 'passes_accurate',
                        'Passes %': 'passes_percentage',
                        'Corner Kicks': 'corner_kicks',
                        'Offsides': 'offsides',
                        'Fouls': 'fouls',
                        'Yellow Cards': 'yellow_cards',
                        'Red Cards': 'red_cards',
                        'Goalkeeper Saves': 'goalkeeper_saves',
                        'expected_goals': 'expected_goals',
                    }
                    
                    if type_name in mapping:
                        key = mapping[type_name]
                        
                        # Processar valor
                        if value is None:
                            stats_dict[key] = None
                        elif isinstance(value, str) and '%' in value:
                            # Remover % e converter
                            stats_dict[key] = int(value.replace('%', ''))
                        else:
                            try:
                                stats_dict[key] = int(value) if value else None
                            except:
                                stats_dict[key] = value
                
                # Adicionar IDs
                stats_dict['fixture_id'] = fixture_id
                stats_dict['team_id'] = team_id
                
                # Guardar na BD
                self.db.insert_fixture_statistics(stats_dict)
            
            print(f"      ✅ Estatísticas guardadas")
            return True
            
        except Exception as e:
            print(f"      ❌ Erro ao processar estatísticas: {e}")
            return False
    
    # ========================================================================
    # PROCESSAMENTO DE EVENTOS
    # ========================================================================
    
    def process_fixture_events(self, fixture_id: int) -> bool:
        """
        Buscar e guardar eventos do jogo (golos, cartões, etc.)
        CRÍTICO para análise de distribuição de golos por minuto
        
        Args:
            fixture_id: ID do jogo
        
        Returns:
            True se guardou com sucesso
        """
        try:
            print(f"   ⚽ Buscando eventos do jogo {fixture_id}...")
            
            # Buscar da API
            events_raw = self.api.get_fixture_events(fixture_id)
            
            if not events_raw:
                print(f"      ⚠️  Sem eventos disponíveis")
                return False
            
            # Processar cada evento
            events_count = 0
            for event in events_raw:
                event_data = {
                    'fixture_id': fixture_id,
                    'team_id': event.get('team', {}).get('id'),
                    'time_elapsed': event.get('time', {}).get('elapsed'),
                    'time_extra': event.get('time', {}).get('extra'),
                    'type': event.get('type'),
                    'detail': event.get('detail'),
                    'player_id': event.get('player', {}).get('id'),
                    'player_name': event.get('player', {}).get('name'),
                    'assist_id': event.get('assist', {}).get('id'),
                    'assist_name': event.get('assist', {}).get('name'),
                    'comments': event.get('comments'),
                }
                
                self.db.insert_fixture_event(event_data)
                events_count += 1
            
            print(f"      ✅ {events_count} eventos guardados")
            return True
            
        except Exception as e:
            print(f"      ❌ Erro ao processar eventos: {e}")
            return False
    
    # ========================================================================
    # CÁLCULO DE MÉTRICAS AVANÇADAS
    # ========================================================================
    
    def calculate_offensive_pressure_score(self, team_id: int, 
                                          league_id: int,
                                          last_n_games: int = 5) -> float:
        """
        Calcular score de pressão ofensiva baseado em estatísticas
        
        Componentes:
        - Shots on goal (peso 30%)
        - Shots insidebox (peso 25%)
        - Corner kicks (peso 20%)
        - Ball possession (peso 15%)
        - Dangerous attacks (peso 10%)
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
            last_n_games: Número de jogos a analisar
        
        Returns:
            Score 0-100
        """
        try:
            # Obter médias das estatísticas
            stats = self.db.get_team_avg_statistics(
                team_id, 
                league_id, 
                CURRENT_SEASON,
                last_n_games
            )
            
            if not stats or stats.get('games_count', 0) < 3:
                return 0
            
            score = 0
            
            # 1. Shots on goal (peso 30%)
            shots_on_goal = stats.get('avg_shots_on_goal', 0) or 0
            if shots_on_goal >= 5:
                score += 30
            elif shots_on_goal >= 3:
                score += 20
            elif shots_on_goal >= 1:
                score += 10
            
            # 2. Shots insidebox (peso 25%)
            shots_inside = stats.get('avg_shots_insidebox', 0) or 0
            if shots_inside >= 8:
                score += 25
            elif shots_inside >= 5:
                score += 15
            elif shots_inside >= 3:
                score += 8
            
            # 3. Corner kicks (peso 20%)
            corners = stats.get('avg_corners', 0) or 0
            if corners >= 5:
                score += 20
            elif corners >= 3:
                score += 12
            elif corners >= 1:
                score += 5
            
            # 4. Ball possession (peso 15%)
            possession = stats.get('avg_possession', 0) or 0
            if possession >= 60:
                score += 15
            elif possession >= 50:
                score += 8
            elif possession >= 40:
                score += 3
            
            # 5. Dangerous attacks (peso 10%)
            dangerous = stats.get('avg_dangerous_attacks', 0) or 0
            if dangerous >= 40:
                score += 10
            elif dangerous >= 30:
                score += 6
            elif dangerous >= 20:
                score += 3
            
            return min(score, 100)
            
        except Exception as e:
            print(f"❌ Erro ao calcular pressão ofensiva: {e}")
            return 0
    
    def calculate_minute_distribution_score(self, team_id: int,
                                           league_id: int) -> float:
        """
        Calcular score baseado na distribuição de golos por minuto
        
        Foco: % de golos marcados na 1ª parte (0-45min)
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
        
        Returns:
            Score 0-100
        """
        try:
            # Obter distribuição de golos
            distribution = self.db.get_goals_by_minute_distribution(
                team_id,
                league_id,
                CURRENT_SEASON
            )
            
            if not distribution:
                return 0
            
            # Percentagem de golos na 1ª parte
            first_half_pct = distribution.get('first_half_percentage', 0)
            
            # Converter percentagem para score
            if first_half_pct >= 45:
                return 100
            elif first_half_pct >= 40:
                return 85
            elif first_half_pct >= 35:
                return 70
            elif first_half_pct >= 30:
                return 55
            elif first_half_pct >= 25:
                return 40
            else:
                return 25
            
        except Exception as e:
            print(f"❌ Erro ao calcular distribuição de minutos: {e}")
            return 0
    
    # ========================================================================
    # ANÁLISE COMPLETA DE JOGO
    # ========================================================================
    
    def fetch_and_analyze_fixture(self, fixture_id: int,
                                  fetch_stats: bool = True,
                                  fetch_events: bool = True) -> Dict:
        """
        Buscar dados completos de um jogo e analisar
        
        Args:
            fixture_id: ID do jogo
            fetch_stats: Se deve buscar estatísticas detalhadas
            fetch_events: Se deve buscar eventos
        
        Returns:
            Dicionário com dados completos
        """
        print(f"\n🔍 Analisando fixture {fixture_id}...")
        
        try:
            # 1. Buscar fixture básico
            fixture_raw = self.api.get_fixture_details(fixture_id)
            
            if not fixture_raw:
                print("❌ Fixture não encontrado")
                return {}
            
            # 2. Guardar fixture
            self.save_fixture_complete(fixture_raw)
            
            # 3. Buscar estatísticas (se o jogo já terminou)
            status = fixture_raw.get('fixture', {}).get('status', {}).get('short')
            
            if status == 'FT' and fetch_stats:
                self.process_fixture_statistics(fixture_id)
            
            # 4. Buscar eventos (se o jogo já terminou)
            if status == 'FT' and fetch_events:
                self.process_fixture_events(fixture_id)
            
            print("✅ Fixture processado com sucesso!")
            
            return self.db.get_fixture(fixture_id)
            
        except Exception as e:
            print(f"❌ Erro ao processar fixture: {e}")
            return {}
    
    def fetch_today_fixtures(self, league_id: int = None) -> List[Dict]:
        """
        Buscar e guardar jogos de hoje
        
        Args:
            league_id: ID da liga (opcional)
        
        Returns:
            Lista de fixtures processados
        """
        print(f"\n📅 Buscando jogos de hoje...")
        
        try:
            # Buscar da API
            fixtures_raw = self.api.get_today_fixtures(league_id)
            
            if not fixtures_raw:
                print("⚠️  Nenhum jogo encontrado para hoje")
                return []
            
            print(f"📋 Encontrados {len(fixtures_raw)} jogos")
            
            # Processar cada fixture
            processed = []
            for fixture_raw in fixtures_raw:
                fixture_id = fixture_raw.get('fixture', {}).get('id')
                
                if self.save_fixture_complete(fixture_raw):
                    fixture_data = self.db.get_fixture(fixture_id)
                    if fixture_data:
                        processed.append(fixture_data)
            
            print(f"✅ {len(processed)} jogos guardados na BD")
            return processed
            
        except Exception as e:
            print(f"❌ Erro ao buscar jogos de hoje: {e}")
            return []
    
    def fetch_team_history(self, team_id: int, league_id: int,
                          last_n_games: int = 10) -> List[Dict]:
        """
        Buscar e guardar histórico de jogos de uma equipa
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
            last_n_games: Número de jogos
        
        Returns:
            Lista de jogos
        """
        print(f"   📥 Buscando histórico da equipa {team_id}...")
        
        try:
            # Buscar da API
            fixtures_raw = self.api.get_team_fixtures(
                team_id,
                last=last_n_games,
                season=CURRENT_SEASON
            )
            
            # Guardar fixtures
            saved = 0
            for fixture_raw in fixtures_raw:
                # Filtrar apenas jogos da liga especificada
                if fixture_raw.get('league', {}).get('id') == league_id:
                    if self.save_fixture_complete(fixture_raw):
                        
                        # Se jogo terminou, buscar stats e eventos
                        status = fixture_raw.get('fixture', {}).get('status', {}).get('short')
                        fixture_id = fixture_raw.get('fixture', {}).get('id')
                        
                        if status == 'FT':
                            self.process_fixture_statistics(fixture_id)
                            self.process_fixture_events(fixture_id)
                        
                        saved += 1
            
            print(f"      ✅ {saved} jogos guardados")
            
            # Retornar da BD
            return self.db.get_team_fixtures(
                team_id,
                league_id=league_id,
                season=CURRENT_SEASON,
                status='FT',
                limit=last_n_games
            )
            
        except Exception as e:
            print(f"      ❌ Erro ao buscar histórico: {e}")
            return []
    
    def fetch_head_to_head(self, team1_id: int, team2_id: int,
                          league_id: int) -> List[Dict]:
        """
        Buscar e guardar confrontos diretos
        
        Args:
            team1_id: ID da primeira equipa
            team2_id: ID da segunda equipa
            league_id: ID da liga
        
        Returns:
            Lista de confrontos
        """
        print(f"   📥 Buscando confrontos diretos...")
        
        try:
            # Buscar da API
            fixtures_raw = self.api.get_head_to_head(
                team1_id,
                team2_id,
                years=ANALYSIS_PARAMS['direct_confrontations_years'],
                league_id=league_id
            )
            
            # Guardar fixtures
            saved = 0
            for fixture_raw in fixtures_raw:
                if self.save_fixture_complete(fixture_raw):
                    
                    # Se jogo terminou, buscar stats e eventos
                    status = fixture_raw.get('fixture', {}).get('status', {}).get('short')
                    fixture_id = fixture_raw.get('fixture', {}).get('id')
                    
                    if status == 'FT':
                        self.process_fixture_statistics(fixture_id)
                        self.process_fixture_events(fixture_id)
                    
                    saved += 1
            
            print(f"      ✅ {saved} confrontos guardados")
            
            # Retornar da BD
            return self.db.get_head_to_head(
                team1_id,
                team2_id,
                league_id=league_id,
                limit=10
            )
            
        except Exception as e:
            print(f"      ❌ Erro ao buscar confrontos: {e}")
            return []

# ============================================================================
# Teste do Data Processor
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTE DO DATA PROCESSOR")
    print("="*80 + "\n")
    
    processor = DataProcessor()
    
    print("\n✅ Data Processor testado com sucesso!")
    print("\n💡 Para testar com dados reais:")
    print("   processor.fetch_today_fixtures(league_id=39)  # Premier League")
    print("="*80 + "\n")