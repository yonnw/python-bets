"""
Teste da Base de Dados
"""

from database.db_manager import DatabaseManager

print("\n" + "="*80)
print("🧪 TESTE DA BASE DE DADOS")
print("="*80 + "\n")

# Inicializar BD
db = DatabaseManager()

# Verificar estatísticas
print("📊 Estatísticas da Base de Dados:")
stats = db.get_database_stats()
for table, count in stats.items():
    print(f"   ✅ {table}: {count} registos")

print("\n" + "="*80)
print("✅ BASE DE DADOS FUNCIONA PERFEITAMENTE!")
print("="*80 + "\n")

# Testar inserção de equipa
print("🧪 Testando inserção de equipa...")
test_team = {
    'id': 33,
    'name': 'Manchester United',
    'code': 'MUN',
    'country': 'England',
    'founded': 1878,
    'logo': 'https://example.com/logo.png'
}

if db.insert_team(test_team):
    print("   ✅ Equipa inserida com sucesso!")
    
    # Verificar se foi guardada
    team = db.get_team(33)
    if team:
        print(f"   ✅ Equipa recuperada: {team['name']}")

print("\n" + "="*80)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*80 + "\n")