"""
Football Betting AI - Análise de Golos na 1ª Parte + Over 1.5 FT
Aplicação principal
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import LEAGUES, CURRENT_SEASON
from database.db_manager import DatabaseManager
from api.api_client import APIFootballClient
from analysis.data_processor import DataProcessor
from analysis.scoring import ScoringSystem

class FootballBettingAI:
    """Aplicação principal de análise de apostas"""
    
    def __init__(self):
        print("🚀 Inicializando Football Betting AI...\n")
        
        self.db = DatabaseManager()
        self.api = APIFootballClient()
        self.processor = DataProcessor()
        self.scoring = ScoringSystem()
        
        print("✅ Sistema inicializado com sucesso!\n")
    
    def analyze_today_matches(self, league_ids: List[int] = None) -> List[Dict]:
        """
        Analisar jogos de hoje
        
        Args:
            league_ids: Lista de IDs das ligas a analisar (None = todas)
        
        Returns:
            Lista de análises dos jogos
        """
        if league_ids is None:
            league_ids = list(LEAGUES.values())
        
        print(f"📅 Analisando jogos de {datetime.now().strftime('%d/%m/%Y')}\n")
        
        all_predictions = []
        
        for league_id in league_ids:
            league_name = [name for name, id in LEAGUES.items() if id == league_id][0]
            print(f"🏆 Liga: {league_name} (ID: {league_id})")
            
            # Buscar jogos de hoje desta liga
            today_fixtures = self.api.get_today_fixtures(league_id)
            
            if not today_fixtures:
                print(f"   ℹ️  Sem jogos hoje nesta liga\n")
                continue
            
            print(f"   📋 Encontrados {len(today_fixtures)} jogos\n")
            
            # Analisar cada jogo
            for fixture in today_fixtures:
                try:
                    prediction = self.analyze_single_match(fixture, league_name)
                    if prediction:
                        all_predictions.append(prediction)
                except Exception as e:
                    print(f"   ❌ Erro ao analisar jogo: {e}\n")
                    continue
        
        # Ordenar por score
        all_predictions.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return all_predictions
    
    def analyze_single_match(self, fixture: Dict, league_name: str) -> Dict:
        """
        Analisar um único jogo
        
        Args:
            fixture: Dados do jogo da API
            league_name: Nome da liga
        
        Returns:
            Dicionário com análise completa
        """
        teams = fixture.get('teams', {})
        fixture_data = fixture.get('fixture', {})
        league_data = fixture.get('league', {})
        
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        home_team_id = home_team.get('id')
        away_team_id = away_team.get('id')
        home_team_name = home_team.get('name')
        away_team_name = away_team.get('name')
        
        print(f"   ⚽ Analisando: {home_team_name} vs {away_team_name}")
        
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
            'overall_score_o15': analysis_result['overall_score_o15'],
            'confidence_level_o15': analysis_result['confidence_level_o15'],
            'h2h_score_o15': analysis_result['h2h_score_o15'],
            'home_form_score_o15': analysis_result['home_form_score_o15'],
            'away_form_score_o15': analysis_result['away_form_score_o15'],
            'recommendation_o15': analysis_result['recommendation_o15'],
            
            'first_half_stats_score': None,
            'reasoning': analysis_result['reasoning']
        }
        
        # Guardar na base de dados
        self.db.insert_prediction(prediction)
        
        # Print resultado
        score_emoji_ht = "🟢" if prediction['overall_score'] >= 75 else "🟡" if prediction['overall_score'] >= 60 else "🔴"
        score_emoji_ft = "🟢" if prediction['overall_score_o15'] >= 75 else "🟡" if prediction['overall_score_o15'] >= 60 else "🔴"
        
        print(f"      {score_emoji_ht} Over 0.5 HT: {prediction['overall_score']}/100 | {prediction['recommendation']}")
        print(f"      {score_emoji_ft} Over 1.5 FT: {prediction['overall_score_o15']}/100 | {prediction['recommendation_o15']}\n")
        
        return prediction
    
    def display_predictions(self, predictions: List[Dict]):
        """
        Mostrar previsões de forma legível
        
        Args:
            predictions: Lista de previsões
        """
        if not predictions:
            print("❌ Sem previsões para apresentar\n")
            return
        
        print("\n" + "="*80)
        print("📊 RESUMO DAS ANÁLISES - JOGOS COM MAIOR PROBABILIDADE")
        print("="*80 + "\n")
        
        # Filtrar apenas recomendações positivas
        recommended = [p for p in predictions if p['recommendation'] in ['SIM', 'TALVEZ']]
        
        if not recommended:
            print("⚠️ Nenhum jogo com recomendação positiva hoje\n")
            return
        
        for i, pred in enumerate(recommended, 1):
            emoji_ht = "🟢" if pred['overall_score'] >= 75 else "🟡"
            emoji_ft = "🟢" if pred['overall_score_o15'] >= 75 else "🟡"
            
            print(f"#{i} - {pred['league_name']}")
            print(f"   {pred['home_team']} vs {pred['away_team']}")
            print(f"   {emoji_ht} Over 0.5 HT: {pred['overall_score']}/100 ({pred['confidence_level']}) - {pred['recommendation']}")
            print(f"   {emoji_ft} Over 1.5 FT: {pred['overall_score_o15']}/100 ({pred['confidence_level_o15']}) - {pred['recommendation_o15']}")
            print(f"   Horário: {datetime.fromisoformat(pred['date'].replace('Z', '+00:00')).strftime('%H:%M')}")
            print()
        
        print("="*80 + "\n")
    
    def display_top_matches(self, predictions: List[Dict], min_score: int = 60):
        """
        Mostrar TOP jogos do dia com score mínimo
        
        Args:
            predictions: Lista de previsões
            min_score: Score mínimo para incluir (default: 60)
        """
        if not predictions:
            print("❌ Sem previsões para apresentar\n")
            return
        
        # Filtrar apenas jogos com score >= min_score
        top_predictions = [p for p in predictions if p['overall_score'] >= min_score]
        
        if not top_predictions:
            print(f"\n⚠️ Nenhum jogo com score ≥ {min_score} encontrado hoje\n")
            return
        
        print("\n" + "="*80)
        print(f"🏆 TOP {len(top_predictions[:10])} JOGOS DO DIA (Score ≥ {min_score})")
        print("="*80 + "\n")
        
        for i, pred in enumerate(top_predictions[:10], 1):  # Top 10
            emoji_ht = "🟢" if pred['overall_score'] >= 75 else "🟡"
            emoji_ft = "🟢" if pred['overall_score_o15'] >= 75 else "🟡"
            
            print(f"#{i} - {pred['league_name']}")
            print(f"   {pred['home_team']} vs {pred['away_team']}")
            print(f"   {emoji_ht} Over 0.5 HT: {pred['overall_score']}/100 ({pred['confidence_level']}) - {pred['recommendation']}")
            print(f"   {emoji_ft} Over 1.5 FT: {pred['overall_score_o15']}/100 ({pred['confidence_level_o15']}) - {pred['recommendation_o15']}")
            
            try:
                date_obj = datetime.fromisoformat(pred['date'].replace('Z', '+00:00'))
                print(f"   Horário: {date_obj.strftime('%H:%M')}")
            except:
                pass
            print()
        
        print("="*80 + "\n")
        
        return top_predictions
    
    def display_detailed_analysis(self, prediction: Dict):
        """
        Mostrar análise detalhada de um jogo com visualização
        
        Args:
            prediction: Previsão do jogo
        """
        print("\n" + "="*80)
        print(f"🔍 ANÁLISE DETALHADA")
        print("="*80)
        print(f"\n🏆 Liga: {prediction['league_name']}")
        print(f"⚽ Jogo: {prediction['home_team']} vs {prediction['away_team']}")
        
        try:
            date_str = prediction['date']
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            print(f"📅 Data: {date_obj.strftime('%d/%m/%Y %H:%M')}")
        except:
            print(f"📅 Data: {prediction['date']}")
        
        print(f"\n{prediction['reasoning']}")
        
        # Buscar dados para visualização
        try:
            home_team_id = None
            away_team_id = None
            
            # Buscar IDs das equipas na BD
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM teams WHERE name = ?", (prediction['home_team'],))
                result = cursor.fetchone()
                if result:
                    home_team_id = result['id']
                
                cursor.execute("SELECT id FROM teams WHERE name = ?", (prediction['away_team'],))
                result = cursor.fetchone()
                if result:
                    away_team_id = result['id']
            
            if home_team_id and away_team_id:
                # 1. Confrontos diretos
                h2h_matches = self.db.get_head_to_head(home_team_id, away_team_id, limit=50)
                
                if h2h_matches:
                    viz = self.scoring.format_h2h_visualization(
                        h2h_matches, 
                        prediction['home_team'], 
                        prediction['away_team']
                    )
                    print(viz)
                
                # 2. Forma da equipa da casa (apenas campeonato)
                league_id = None
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM leagues WHERE name = ?", (prediction['league_name'],))
                    result = cursor.fetchone()
                    if result:
                        league_id = result['id']

                if league_id:
                    home_matches = self.db.get_team_recent_matches_by_league(home_team_id, league_id, limit=10)
                else:
                    home_matches = self.db.get_team_recent_matches(home_team_id, limit=10)
                
                if home_matches:
                    viz_home = self.scoring.format_team_form_visualization(
                        home_matches,
                        prediction['home_team'],
                        home_team_id,
                        is_home=True
                    )
                    print(viz_home)
                
                # 3. Forma da equipa visitante (apenas campeonato)
                if league_id:
                    away_matches = self.db.get_team_recent_matches_by_league(away_team_id, league_id, limit=10)
                else:
                    away_matches = self.db.get_team_recent_matches(away_team_id, limit=10)
                
                if away_matches:
                    viz_away = self.scoring.format_team_form_visualization(
                        away_matches,
                        prediction['away_team'],
                        away_team_id,
                        is_home=False
                    )
                    print(viz_away)
                    
        except Exception as e:
            print(f"\n   ⚠️ Erro ao carregar visualização: {e}")
        
        print("\n" + "="*80 + "\n")

    def check_api_status(self):
        """Verificar status da API"""
        self.api.print_api_status()

def main():
    """Função principal"""
    print("\n" + "="*80)
    print("⚽ FOOTBALL BETTING AI - ANÁLISE OVER 0.5 HT + OVER 1.5 FT")
    print("="*80 + "\n")
    
    # Inicializar aplicação
    app = FootballBettingAI()
    
    # Verificar API
    print("\n📡 Verificando status da API...")
    app.check_api_status()
    
    # Menu interativo
    while True:
        print("\n" + "-"*80)
        print("MENU PRINCIPAL")
        print("-"*80)
        print("1. 🏆 TOP JOGOS DO DIA (Melhores scores)")
        print("2. Analisar jogos de hoje (todas as ligas)")
        print("3. Analisar liga específica")
        print("4. Ver previsões guardadas de hoje")
        print("5. Verificar status da API")
        print("6. Sair")
        print("-"*80)

        choice = input("\nEscolha uma opção (1-6): ").strip()

        if choice == '1':
            # TOP JOGOS DO DIA
            print("\n🔎 Analisando TODAS as ligas para encontrar os melhores jogos...\n")
            predictions = app.analyze_today_matches()
            
            if predictions:
                top_predictions = app.display_top_matches(predictions, min_score=60)
                
                if top_predictions:
                    # Opção de ver detalhes
                    detail = input("Deseja ver análise detalhada de algum jogo? (s/n): ").strip().lower()
                    if detail == 's':
                        try:
                            idx = int(input(f"Qual jogo? (1-{min(len(top_predictions), 10)}): ")) - 1
                            if 0 <= idx < len(top_predictions):
                                app.display_detailed_analysis(top_predictions[idx])
                        except:
                            print("⚠️ Opção inválida")
            else:
                print("\n❌ Nenhum jogo encontrado para hoje")
        
        elif choice == '2':
            # Analisar todas as ligas
            predictions = app.analyze_today_matches()
            app.display_predictions(predictions)
            
            if predictions:
                detail = input("\nDeseja ver análise detalhada de algum jogo? (s/n): ").strip().lower()
                if detail == 's':
                    try:
                        idx = int(input(f"Qual jogo? (1-{len(predictions)}): ")) - 1
                        if 0 <= idx < len(predictions):
                            app.display_detailed_analysis(predictions[idx])
                    except:
                        print("⚠️ Opção inválida")
        
        elif choice == '3':
            # Analisar liga específica
            print("\nLigas disponíveis:")
            for i, (name, league_id) in enumerate(LEAGUES.items(), 1):
                print(f"  {i}. {name} (ID: {league_id})")
            
            try:
                league_choice = int(input("\nEscolha a liga (1-7): ")) - 1
                league_id = list(LEAGUES.values())[league_choice]
                predictions = app.analyze_today_matches([league_id])
                app.display_predictions(predictions)
                
                if predictions:
                    detail = input("\nDeseja ver análise detalhada de algum jogo? (s/n): ").strip().lower()
                    if detail == 's':
                        try:
                            idx = int(input(f"Qual jogo? (1-{len(predictions)}): ")) - 1
                            if 0 <= idx < len(predictions):
                                app.display_detailed_analysis(predictions[idx])
                        except:
                            print("⚠️ Opção inválida")
            except:
                print("⚠️ Opção inválida")
        
        elif choice == '4':
            # Ver previsões guardadas
            predictions = app.db.get_today_predictions()
            if predictions:
                app.display_predictions(predictions)
            else:
                print("\n❌ Sem previsões guardadas para hoje")
        
        elif choice == '5':
            # Verificar status da API
            app.check_api_status()
        
        elif choice == '6':
            # Sair
            print("\n👋 Até breve!\n")
            break
        
        else:
            print("\n⚠️ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()