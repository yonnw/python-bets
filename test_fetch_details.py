"""
Teste - Buscar estatísticas e eventos de um jogo específico
"""

from analysis.data_processor import DataProcessor
from database.db_manager import DatabaseManager

print("\n" + "="*80)
print("🔍 TESTE: Buscar Estatísticas e Eventos Detalhados")
print("="*80 + "\n")

# Inicializar
processor = DataProcessor()
db = DatabaseManager()

# ============================================================================
# Buscar um jogo da Premier League (ID: 39) que já terminou
# ============================================================================
print("🔍 Buscando um jogo que já terminou...")

# Pegar fixtures que já terminaram
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM fixtures 
        WHERE status_short = 'FT'
        LIMIT 1
    """)
    row = cursor.fetchone()
    
    if row:
        fixture = dict(row)
        fixture_id = fixture['id']
        print(f"✅ Jogo encontrado: ID {fixture_id}")
        print(f"   Status: {fixture['status_short']}")
        print(f"   Liga ID: {fixture['league_id']}")
    else:
        print("❌ Nenhum jogo finalizado encontrado")
        exit()

# ============================================================================
# Buscar estatísticas detalhadas
# ============================================================================
print(f"\n📊 Buscando estatísticas do jogo {fixture_id}...")

if processor.process_fixture_statistics(fixture_id):
    stats = db.get_fixture_statistics(fixture_id)
    print(f"✅ Estatísticas guardadas: {len(stats)} equipas")
    
    if stats:
        for team_stat in stats:
            print(f"\n   Equipa ID: {team_stat['team_id']}")
            print(f"   • Shots on goal: {team_stat.get('shots_on_goal', 'N/A')}")
            print(f"   • Corner kicks: {team_stat.get('corner_kicks', 'N/A')}")
            print(f"   • Ball possession: {team_stat.get('ball_possession', 'N/A')}%")

# ============================================================================
# Buscar eventos (golos com minuto exato)
# ============================================================================
print(f"\n⚽ Buscando eventos do jogo {fixture_id}...")

if processor.process_fixture_events(fixture_id):
    events = db.get_fixture_events(fixture_id, event_type='Goal')
    print(f"✅ Eventos guardados!")
    print(f"   🎯 Golos encontrados: {len(events)}")
    
    if events:
        print("\n   Golos por minuto:")
        for event in events[:5]:  # Mostrar 5 primeiros
            print(f"   • Min {event['time_elapsed']}: {event.get('player_name', 'Unknown')}")

# ============================================================================
# Verificar BD novamente
# ============================================================================
print("\n" + "="*80)
print("📊 DADOS NA BASE DE DADOS")
print("="*80 + "\n")

stats = db.get_database_stats()
for table, count in stats.items():
    emoji = "✅" if count > 0 else "⚪"
    print(f"   {emoji} {table}: {count} registos")

print("\n" + "="*80)
print("🎉 TESTE DE ESTATÍSTICAS COMPLETO!")
print("="*80 + "\n")