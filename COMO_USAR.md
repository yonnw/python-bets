# 🎯 Football Betting AI - Como Usar

## ✅ Sistema Completo e Funcional!

### 📦 O que temos:

1. **Base de Dados SQLite** - Armazena tudo
2. **API Client** - Busca dados da API Football
3. **Data Processor** - Processa e calcula métricas
4. **Scoring System** - Avalia probabilidade de golos

---

## 🚀 Como Usar

### 1️⃣ **Buscar Jogos de Hoje**
```python
from analysis.data_processor import DataProcessor

processor = DataProcessor()

# Buscar todos os jogos de hoje
fixtures = processor.fetch_today_fixtures()

# Ou filtrar por liga
fixtures_pl = processor.fetch_today_fixtures(league_id=39)  # Premier League
```

### 2️⃣ **Analisar um Jogo Específico**
```python
# Buscar dados completos de um jogo
fixture_data = processor.fetch_and_analyze_fixture(
    fixture_id=1234567,
    fetch_stats=True,
    fetch_events=True
)
```

### 3️⃣ **Calcular Score de um Jogo**
```python
from analysis.scoring import ScoringSystem
from database.db_manager import DatabaseManager

scoring = ScoringSystem()
db = DatabaseManager()

# Preparar dados para análise
analysis_data = {
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
    # Adicionar pressão ofensiva e distribuição
    'home_pressure': processor.calculate_offensive_pressure_score(
        team_id=33, league_id=39
    ),
    'home_distribution': db.get_goals_by_minute_distribution(
        team_id=33, league_id=39
    )
}

# Calcular score
result = scoring.analyze_match(analysis_data)

print(f"Score Over 0.5 HT: {result['overall_score']}/100")
print(f"Recomendação: {result['recommendation']}")
```

### 4️⃣ **Verificar Base de Dados**
```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Ver estatísticas
stats = db.get_database_stats()
print(stats)

# Ver jogos de hoje
fixtures_today = db.get_fixtures_by_date('2025-10-25')
```

---

## 📊 Componentes do Score

### Over 0.5 HT (Golo na 1ª Parte):

| Componente | Peso | O que avalia |
|------------|------|--------------|
| H2H | 25% | Confrontos diretos |
| Forma Casa | 20% | Últimos jogos em casa |
| Forma Fora | 20% | Últimos jogos fora |
| **Pressão Ofensiva** | 20% | Shots, corners, posse |
| **Distribuição Minutos** | 15% | % golos na 1ª parte |

### Over 1.5 FT (2+ Golos):

| Componente | Peso | O que avalia |
|------------|------|--------------|
| H2H | 30% | Confrontos diretos |
| Forma Casa | 25% | Últimos jogos |
| Forma Fora | 25% | Últimos jogos |
| Pressão Ofensiva | 20% | Capacidade ofensiva |

---

## 🎯 Níveis de Confiança

- **ALTA** (≥75): Forte indicação - Recomendação **SIM**
- **MÉDIA** (60-74): Probabilidade moderada - **TALVEZ**
- **BAIXA** (45-59): Baixa probabilidade - **TALVEZ**
- **MUITO BAIXA** (<45): Não recomendado - **NÃO**

---

## 💡 Próximos Desenvolvimentos

1. ✅ Sistema base funcional
2. ⏳ Integrar no main.py
3. ⏳ Análise automática diária
4. ⏳ Sistema de notificações
5. ⏳ Dashboard web
6. ⏳ Machine Learning para ajuste de pesos

---

## 📞 Estrutura de Ficheiros
```
football_betting_ai/
├── config/
│   └── config.py              ✅ Configurações
├── database/
│   ├── db_schema.sql          ✅ Schema SQL
│   ├── db_manager.py          ✅ Gestor BD
│   └── football_betting.db    ✅ Base de dados
├── api/
│   └── api_client.py          ✅ Cliente API
├── analysis/
│   ├── data_processor.py      ✅ Processador
│   └── scoring.py             ✅ Scoring System
├── test_*.py                  ✅ Testes
└── .env                       ✅ API Key
```

---

## 🎉 Sistema 100% Funcional!

Tudo está pronto para começar a analisar jogos reais!