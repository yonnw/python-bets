"""
Script de teste para verificar componentes do sistema
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Testar base de dados"""
    print("🧪 Testando Base de Dados...")
    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        print("   ✅ Base de dados inicializada com sucesso!")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_config():
    """Testar configurações"""
    print("\n🧪 Testando Configurações...")
    try:
        from config.config import LEAGUES, API_KEY, CURRENT_SEASON
        print(f"   ✅ Configurações carregadas")
        print(f"   📊 Ligas configuradas: {len(LEAGUES)}")
        print(f"   📅 Temporada: {CURRENT_SEASON}")
        
        if API_KEY == "YOUR_API_KEY_HERE":
            print("   ⚠️  API Key não configurada! Por favor, edite config/config.py ou .env")
            return False
        else:
            print("   ✅ API Key configurada")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_api_client():
    """Testar cliente da API"""
    print("\n🧪 Testando Cliente da API...")
    try:
        from api.api_client import APIFootballClient
        client = APIFootballClient()
        print("   ✅ Cliente criado com sucesso")
        
        # Nota: Não vamos fazer requests reais no teste para não gastar créditos
        print("   ℹ️  Para testar a conexão real, execute: python api/api_client.py")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_data_processor():
    """Testar processador de dados"""
    print("\n🧪 Testando Processador de Dados...")
    try:
        from analysis.fail_data_processor import DataProcessor
        processor = DataProcessor()
        print("   ✅ Processador inicializado com sucesso")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_scoring_system():
    """Testar sistema de scoring"""
    print("\n🧪 Testando Sistema de Scoring...")
    try:
        from analysis.fail_scoring import ScoringSystem
        scoring = ScoringSystem()
        print("   ✅ Sistema de scoring inicializado")
        
        # Teste com dados fictícios
        test_data = {
            'h2h': {
                'stats': {
                    'total_matches': 5,
                    'matches_with_first_half_goal': 4,
                    'first_half_goal_percentage': 80,
                    'avg_first_half_goals': 1.4
                }
            },
            'home_team': {
                'stats': {
                    'games_played': 10,
                    'games_with_first_half_goal': 7,
                    'first_half_goal_percentage': 70,
                    'avg_goals_first_half': 0.9
                }
            },
            'away_team': {
                'stats': {
                    'games_played': 10,
                    'games_with_first_half_goal': 6,
                    'first_half_goal_percentage': 60,
                    'avg_goals_first_half': 0.7
                }
            }
        }
        
        result = scoring.analyze_match(test_data)
        print(f"   ✅ Teste de análise concluído")
        print(f"   📊 Score gerado: {result['overall_score']}/100")
        print(f"   🎯 Confiança: {result['confidence_level']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("\n" + "="*80)
    print("⚽ FOOTBALL BETTING AI - TESTES DO SISTEMA")
    print("="*80 + "\n")
    
    tests = [
        test_config,
        test_database,
        test_api_client,
        test_data_processor,
        test_scoring_system
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*80)
    print(f"📊 RESULTADOS: {passed} ✅ | {failed} ❌")
    print("="*80 + "\n")
    
    if failed == 0:
        print("🎉 Todos os testes passaram! O sistema está pronto para usar.")
        print("\n💡 Próximos passos:")
        print("   1. Configure a sua API key em config/config.py ou .env")
        print("   2. Execute: python main.py")
    else:
        print("⚠️  Alguns testes falharam. Por favor, verifique os erros acima.")
        print("\n💡 Dicas:")
        print("   - Certifique-se de que todas as dependências estão instaladas")
        print("   - Verifique se a API key está configurada corretamente")

if __name__ == "__main__":
    main()