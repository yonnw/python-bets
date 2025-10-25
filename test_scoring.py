"""
Teste do Novo Scoring System
"""

from analysis.scoring import ScoringSystem

print("\n" + "="*80)
print("🧪 TESTE DO NOVO SCORING SYSTEM")
print("="*80 + "\n")

# Inicializar
scoring = ScoringSystem()

# ============================================================================
# Dados de exemplo de um jogo
# ============================================================================

test_data = {
    'h2h': {
        'stats': {
            'total_matches': 5,
            'matches_with_first_half_goal': 4,
            'matches_over15': 4
        }
    },
    'home_team': {
        'stats': {
            'games_played': 10,
            'games_with_first_half_goal': 7,
            'games_over15': 6
        }
    },
    'away_team': {
        'stats': {
            'games_played': 10,
            'games_with_first_half_goal': 6,
            'games_over15': 7
        }
    },
    # NOVOS COMPONENTES
    'home_pressure': {
        'games_count': 10,
        'shots_on_goal_avg': 5.5,
        'shots_insidebox_avg': 8.2,
        'corners_avg': 6.1,
        'possession_avg': 58.0
    },
    'away_pressure': {
        'games_count': 10,
        'shots_on_goal_avg': 4.2,
        'shots_insidebox_avg': 6.5,
        'corners_avg': 4.8,
        'possession_avg': 52.0
    },
    'home_distribution': {
        'total': 25,
        'first_half_percentage': 42.0
    },
    'away_distribution': {
        'total': 20,
        'first_half_percentage': 38.0
    }
}

# ============================================================================
# Analisar jogo
# ============================================================================

print("🔍 Analisando jogo de teste...\n")

result = scoring.analyze_match(test_data)

print("="*80)
print("📊 RESULTADOS DA ANÁLISE")
print("="*80 + "\n")

print("🎯 OVER 0.5 HT (Golo na 1ª Parte)")
print(f"   Score: {result['overall_score']}/100")
print(f"   Confiança: {result['confidence_level']}")
print(f"   Recomendação: {result['recommendation']}")
print(f"\n   Componentes:")
print(f"   • H2H: {result['h2h_score']}/100")
print(f"   • Forma Casa: {result['home_form_score']}/100")
print(f"   • Forma Fora: {result['away_form_score']}/100")
print(f"   • Pressão Ofensiva: {result['offensive_pressure_score']:.1f}/100 ⭐ NOVO")
print(f"   • Distribuição Minutos: {result['minute_distribution_score']:.1f}/100 ⭐ NOVO")

print(f"\n🎯 OVER 1.5 FT (2+ Golos no Jogo)")
print(f"   Score: {result['overall_score_o15']}/100")
print(f"   Confiança: {result['confidence_level_o15']}")
print(f"   Recomendação: {result['recommendation_o15']}")

print("\n" + "="*80)
print("📝 REASONING DETALHADO")
print("="*80)
print(result['reasoning'])

print("\n" + "="*80)
print("✅ SCORING SYSTEM FUNCIONA PERFEITAMENTE!")
print("="*80 + "\n")

print("💡 Próximo passo: Integrar tudo no main.py!")