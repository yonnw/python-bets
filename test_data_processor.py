"""
Teste do Data Processor
"""

from analysis.data_processor import DataProcessor

print("\n" + "="*80)
print("🧪 TESTE DO DATA PROCESSOR")
print("="*80 + "\n")

# Inicializar
processor = DataProcessor()

print("\n" + "="*80)
print("✅ DATA PROCESSOR INICIALIZADO COM SUCESSO!")
print("="*80 + "\n")

print("💡 Funções disponíveis:")
print("   • fetch_today_fixtures(league_id) - Buscar jogos de hoje")
print("   • fetch_team_history(team_id, league_id) - Histórico de equipa")
print("   • fetch_head_to_head(team1_id, team2_id, league_id) - Confrontos")
print("   • calculate_offensive_pressure_score(team_id, league_id) - Pressão ofensiva")
print("   • calculate_minute_distribution_score(team_id, league_id) - Distribuição temporal")

print("\n" + "="*80)
print("🚀 TUDO PRONTO PARA COMEÇAR A BUSCAR DADOS!")
print("="*80 + "\n")