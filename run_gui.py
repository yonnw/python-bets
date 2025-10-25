"""
Launcher para Football Betting AI com Interface Gráfica
Integra o sistema existente com a nova GUI
"""

import sys
import os
from datetime import datetime

# Adicionar paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar sistema existente (adaptar conforme sua estrutura)
try:
    from config.config import LEAGUES, CURRENT_SEASON
    from database.db_manager import DatabaseManager
    from api.api_client import APIFootballClient
    from analysis.data_processor import DataProcessor
    from analysis.scoring import ScoringSystem
except ImportError as e:
    print(f"⚠️ Erro ao importar módulos: {e}")
    print("Verifique se os arquivos existem na estrutura do projeto")

# Importar GUI
from gui_app import run_gui

class FootballBettingAI:
    """Aplicação principal - Adaptador para GUI"""
    
    def __init__(self):
        print("🚀 Inicializando Football Betting AI com GUI...\n")
        
        try:
            self.db = DatabaseManager()
            self.api = APIFootballClient()
            self.processor = DataProcessor()
            self.scoring = ScoringSystem()
            
            print("✅ Sistema inicializado com sucesso!\n")
        except Exception as e:
            print(f"❌ Erro ao inicializar: {e}")
            raise
    
    def analyze_today_matches(self, league_ids=None):
        """
        Analisar jogos de hoje
        
        Args:
            league_ids: Lista de IDs das ligas (None = todas)
        
        Returns:
            Lista de previsões
        """
        if league_ids is None:
            league_ids = list(LEAGUES.values())
        
        print(f"📅 Analisando jogos de {datetime.now().strftime('%d/%m/%Y')}")
        
        all_predictions = []
        
        for league_id in league_ids:
            try:
                league_name = [name for name, id in LEAGUES.items() if id == league_id][0]
                print(f"\n🏆 Liga: {league_name}")
                
                # Buscar jogos de hoje
                today_fixtures = self.api.get_today_fixtures(league_id)
                
                if not today_fixtures:
                    print(f"   ℹ️  Sem jogos hoje")
                    continue
                
                print(f"   📋 Encontrados {len(today_fixtures)} jogos")
                
                # Analisar cada jogo
                for fixture in today_fixtures:
                    try:
                        prediction = self.analyze_single_match(fixture, league_name)
                        if prediction:
                            all_predictions.append(prediction)
                    except Exception as e:
                        print(f"   ❌ Erro ao analisar jogo: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Erro na liga {league_id}: {e}")
                continue
        
        # Ordenar por score
        all_predictions.sort(key=lambda x: x['overall_score'], reverse=True)
        
        print(f"\n✅ Análise concluída! {len(all_predictions)} jogos analisados")
        
        return all_predictions
    
    def analyze_single_match(self, fixture, league_name):
        """Analisar um único jogo"""
        teams = fixture.get('teams', {})
        fixture_data = fixture.get('fixture', {})
        league_data = fixture.get('league', {})
        
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        home_team_id = home_team.get('id')
        away_team_id = away_team.get('id')
        home_team_name = home_team.get('name')
        away_team_name = away_team.get('name')
        
        print(f"   ⚽ {home_team_name} vs {away_team_name}")
        
        # Obter dados de análise
        analysis_data = self.processor.get_match_analysis_data(
            home_team_id,
            away_team_id,
            league_data.get('id')
        )
        
        # Calcular score
        analysis_result = self.scoring.analyze_match(analysis_data)
        
        # Criar previsão
        prediction = {
            'match_id': fixture_data.get('id'),
            'date': fixture_data.get('date'),
            'league_name': league_name,
            'home_team': home_team_name,
            'away_team': away_team_name,
            
            # Over 0.5 HT
            'overall_score': analysis_result['overall_score'],
            'confidence_level': analysis_result['confidence_level'],
            'h2h_score': analysis_result['h2h_score'],
            'home_form_score': analysis_result['home_form_score'],
            'away_form_score': analysis_result['away_form_score'],
            'recommendation': analysis_result['recommendation'],
            
            # Over 1.5 FT
            'overall_score_o15': analysis_result.get('overall_score_o15', 0),
            'confidence_level_o15': analysis_result.get('confidence_level_o15', 'N/A'),
            'h2h_score_o15': analysis_result.get('h2h_score_o15', 0),
            'home_form_score_o15': analysis_result.get('home_form_score_o15', 0),
            'away_form_score_o15': analysis_result.get('away_form_score_o15', 0),
            'recommendation_o15': analysis_result.get('recommendation_o15', 'N/A'),
            
            'first_half_stats_score': None,
            'reasoning': analysis_result['reasoning'],
            
            # Status para tracking (futuro)
            'status': 'pending'  # pending, correct, wrong
        }
        
        # Guardar na BD
        try:
            self.db.insert_prediction(prediction)
        except Exception as e:
            print(f"      ⚠️ Erro ao guardar previsão: {e}")
        
        return prediction


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("⚽ FOOTBALL BETTING AI - INTERFACE GRÁFICA v2.0")
    print("="*80 + "\n")
    
    try:
        # Inicializar sistema backend
        app = FootballBettingAI()
        
        # Iniciar GUI
        print("🎨 Iniciando interface gráfica...")
        run_gui(app)
        
    except KeyboardInterrupt:
        print("\n\n👋 Até breve!")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()