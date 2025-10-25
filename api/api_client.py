"""
Cliente para integração com API Football
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import (
    API_FOOTBALL_BASE_URL, 
    API_KEY, 
    API_REQUESTS_PER_MINUTE,
    CURRENT_SEASON
)

class APIFootballClient:
    """Cliente para comunicação com API-Football"""
    
    def __init__(self, api_key: str = API_KEY):
        self.base_url = API_FOOTBALL_BASE_URL
        self.api_key = api_key
        self.headers = {
            'x-apisports-key': self.api_key
        }
        self.request_count = 0
        self.last_request_time = None
        self.rate_limit_delay = 60 / API_REQUESTS_PER_MINUTE  # segundos entre requests
    
    def _rate_limit(self):
        """Controlo de rate limiting"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Fazer request à API com tratamento de erros"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errors'):
                print(f"⚠️ API retornou erros: {data['errors']}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao fazer request: {e}")
            return None
    
    def get_fixtures_by_date(self, date: str, league_id: int = None, 
                            season: int = CURRENT_SEASON) -> List[Dict]:
        """
        Obter jogos por data
        
        Args:
            date: Data no formato YYYY-MM-DD
            league_id: ID da liga (opcional)
            season: Temporada (default: atual)
        
        Returns:
            Lista de jogos
        """
        params = {
            'date': date,
            'season': season
        }
        
        if league_id:
            params['league'] = league_id
        
        data = self._make_request('fixtures', params)
        
        if data and data.get('response'):
            return data['response']
        
        return []
    
    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """
        Obter detalhes de um jogo específico
        
        Args:
            fixture_id: ID do jogo
        
        Returns:
            Detalhes do jogo
        """
        params = {'id': fixture_id}
        data = self._make_request('fixtures', params)
        
        if data and data.get('response'):
            return data['response'][0] if data['response'] else None
        
        return None
    
    def get_fixture_statistics(self, fixture_id: int) -> List[Dict]:
        """
        Obter estatísticas detalhadas de um jogo
        
        Args:
            fixture_id: ID do jogo
        
        Returns:
            Estatísticas do jogo
        """
        params = {'fixture': fixture_id}
        data = self._make_request('fixtures/statistics', params)
        
        if data and data.get('response'):
            return data['response']
        
        return []
    
    def get_head_to_head(self, team1_id: int, team2_id: int, 
                    years: int = 3, league_id: int = None) -> List[Dict]:
        """
        Obter confrontos diretos entre duas equipas nos últimos X anos
        
        Args:
            team1_id: ID da primeira equipa
            team2_id: ID da segunda equipa
            years: Número de anos a analisar (default: 3)
            league_id: ID da liga para filtrar (opcional)
        
        Returns:
            Lista de confrontos diretos
        """
        all_fixtures = []
        
        # Buscar para cada temporada dos últimos X anos
        for year in range(CURRENT_SEASON, CURRENT_SEASON - years, -1):
            params = {
                'h2h': f"{team1_id}-{team2_id}",
                'season': year
            }
            
            # Adicionar filtro de liga se fornecido
            if league_id:
                params['league'] = league_id
            
            data = self._make_request('fixtures/headtohead', params)
            
            if data and data.get('response'):
                all_fixtures.extend(data['response'])
        
        return all_fixtures
    
    def get_team_fixtures(self, team_id: int, last: int = 10, 
                         season: int = CURRENT_SEASON) -> List[Dict]:
        """
        Obter últimos jogos de uma equipa
        
        Args:
            team_id: ID da equipa
            last: Número de últimos jogos (default: 10)
            season: Temporada (default: atual)
        
        Returns:
            Lista de jogos da equipa
        """
        params = {
            'team': team_id,
            'season': season,
            'last': last
        }
        
        data = self._make_request('fixtures', params)
        
        if data and data.get('response'):
            return data['response']
        
        return []
    
    def get_team_fixtures_by_league(self, team_id: int, league_id: int,
                                   season: int = CURRENT_SEASON) -> List[Dict]:
        """
        Obter jogos de uma equipa numa liga específica
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
            season: Temporada (default: atual)
        
        Returns:
            Lista de jogos da equipa na liga
        """
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('fixtures', params)
        
        if data and data.get('response'):
            return data['response']
        
        return []
    
    def get_team_statistics(self, team_id: int, league_id: int, 
                           season: int = CURRENT_SEASON) -> Optional[Dict]:
        """
        Obter estatísticas da equipa na temporada
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
            season: Temporada (default: atual)
        
        Returns:
            Estatísticas da equipa
        """
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('teams/statistics', params)
        
        if data and data.get('response'):
            return data['response']
        
        return None
    
    def get_league_fixtures(self, league_id: int, season: int = CURRENT_SEASON, 
                           from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Obter jogos de uma liga
        
        Args:
            league_id: ID da liga
            season: Temporada (default: atual)
            from_date: Data inicial (YYYY-MM-DD)
            to_date: Data final (YYYY-MM-DD)
        
        Returns:
            Lista de jogos da liga
        """
        params = {
            'league': league_id,
            'season': season
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        data = self._make_request('fixtures', params)
        
        if data and data.get('response'):
            return data['response']
        
        return []
    
    def get_today_fixtures(self, league_id: int = None) -> List[Dict]:
        """
        Obter jogos de hoje
        
        Args:
            league_id: ID da liga (opcional, para filtrar)
        
        Returns:
            Lista de jogos de hoje
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_fixtures_by_date(today, league_id, season=CURRENT_SEASON)
    
    def get_api_status(self) -> Dict:
        """
        Verificar status da API e uso de requests
        
        Returns:
            Informações sobre a conta API
        """
        data = self._make_request('status')
        
        if data:
            return data.get('response', {})
        
        return {}
    
    def print_api_status(self):
        """Imprimir status da API de forma legível"""
        status = self.get_api_status()
        
        if status:
            print("\n📊 Status da API Football:")
            print(f"   Plano: {status.get('subscription', {}).get('plan', 'N/A')}")
            print(f"   Requests hoje: {status.get('requests', {}).get('current', 0)}")
            print(f"   Limite diário: {status.get('requests', {}).get('limit_day', 0)}")
            print(f"   Requests nesta sessão: {self.request_count}")
        else:
            print("❌ Não foi possível obter status da API")
            
    def get_fixture_events(self, fixture_id: int) -> List[Dict]:
        """
        Obter eventos de um jogo (golos, cartões, substituições)
        CRÍTICO para análise de distribuição de golos por minuto
        
        Args:
            fixture_id: ID do jogo
        
        Returns:
            Lista de eventos com minuto exato
        """
        params = {'fixture': fixture_id}
        data = self._make_request('fixtures/events', params)
        
        if data and data.get('response'):
            return data['response']
        
        return []
    
    def get_team_season_statistics(self, team_id: int, league_id: int,
                                   season: int = CURRENT_SEASON) -> Optional[Dict]:
        """
        Obter estatísticas completas da equipa na temporada
        Inclui: golos por minuto, forma, performance casa/fora
        
        Args:
            team_id: ID da equipa
            league_id: ID da liga
            season: Temporada (default: atual)
        
        Returns:
            Dicionário com estatísticas completas da temporada
        """
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('teams/statistics', params)
        
        if data and data.get('response'):
            return data['response']
        
        return None
    
    def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """
        Obter previsões da própria API para um jogo
        Útil para comparar com as nossas previsões
        
        Args:
            fixture_id: ID do jogo
        
        Returns:
            Dicionário com previsões da API
        """
        params = {'fixture': fixture_id}
        data = self._make_request('predictions', params)
        
        if data and data.get('response'):
            return data['response'][0] if data['response'] else None
        
        return None

if __name__ == "__main__":
    # Teste da API
    print("🧪 Testando conexão com API Football...\n")
    
    # Nota: É necessário definir a variável de ambiente API_FOOTBALL_KEY
    # ou editar o config.py com a sua chave
    
    client = APIFootballClient()
    
    # Verificar status da API
    client.print_api_status()
    
    # Testar obtenção de jogos de hoje
    print("\n🔍 Buscando jogos de hoje...")
    today_fixtures = client.get_today_fixtures()
    
    if today_fixtures:
        print(f"✅ Encontrados {len(today_fixtures)} jogos hoje")
        if today_fixtures:
            first = today_fixtures[0]
            print(f"\nExemplo de jogo:")
            print(f"   {first['teams']['home']['name']} vs {first['teams']['away']['name']}")
            print(f"   Liga: {first['league']['name']}")
            print(f"   Horário: {first['fixture']['date']}")
    else:
        print("⚠️ Nenhum jogo encontrado para hoje")