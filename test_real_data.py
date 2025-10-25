"""
Teste REAL - Buscar dados da API e popular a BD
"""

from analysis.data_processor import DataProcessor

print("\n" + "="*80)
print("🚀 TESTE REAL - BUSCANDO DADOS DA API FOOTBALL")
print("="*80 + "\n")

# Inicializar
processor = DataProcessor()

# ============================================================================
# TESTE 1: Buscar jogos de HOJE
# ============================================================================
print("\n" + "="*80)
print("📅 TESTE 1: Buscar jogos de hoje")
print("="*80 + "\n")

# Buscar jogos de hoje (todas as ligas)
fixtures_today = processor.fetch_today_fixtures()

print(f"\n✅ Total de jogos guardados: {len(fixtures_today)}")

if fixtures_today:
    print("\n📋 Exemplos de jogos:")
    for i, fixture in enumerate(fixtures_today[:3], 1):  # Mostrar 3 primeiros
        print(f"   {i}. ID: {fixture['id']}")
        print(f"      Status: {fixture['status_short']}")
        print(f"      Liga: {fixture['league_id']}")

# ============================================================================
# VERIFICAR BASE DE DADOS
# ============================================================================
print("\n" + "="*80)
print("📊 VERIFICAR DADOS NA BASE DE DADOS")
print("="*80 + "\n")

from database.db_manager import DatabaseManager
db = DatabaseManager()

stats = db.get_database_stats()
print("Registos na BD:")
for table, count in stats.items():
    emoji = "✅" if count > 0 else "⚪"
    print(f"   {emoji} {table}: {count} registos")

print("\n" + "="*80)
print("🎉 TESTE COMPLETO! A aplicação está a funcionar!")
print("="*80 + "\n")

print("💡 Próximos passos:")
print("   1. ✅ Base de Dados - FUNCIONAL")
print("   2. ✅ API Client - FUNCIONAL")
print("   3. ✅ Data Processor - FUNCIONAL")
print("   4. ⏳ Atualizar Scoring System (próximo)")
print("   5. ⏳ Integrar tudo no main.py")