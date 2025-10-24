# Football Betting AI - Análise de Golos na 1ª Parte

## Objetivo
Analisar jogos diários para identificar partidas com alta probabilidade de golo na primeira parte.

## Ligas Analisadas
- Premier League (ID: 39)
- La Liga (ID: 140)
- Bundesliga (ID: 78)
- Serie A (ID: 135)
- Ligue 1 (ID: 61)
- Primeira Liga (ID: 94)

## Critérios de Análise
1. Confrontos diretos (últimos 5 jogos)
2. Forma recente (últimos 10 jogos de cada equipa)
3. Estatísticas de golos na 1ª parte
4. Desempenho casa/fora

## Stack Tecnológica
- Python 3.10+
- SQLite (base de dados)
- Pandas (manipulação de dados)
- Scikit-learn (machine learning)
- Requests (API calls)

## Estrutura do Projeto
```
football_betting_ai/
├── config/
│   └── config.py
├── database/
│   ├── models.py
│   └── db_manager.py
├── api/
│   ├── api_client.py
│   └── endpoints.py
├── analysis/
│   ├── data_processor.py
│   ├── scoring.py
│   └── ml_model.py
├── utils/
│   └── helpers.py
├── main.py
└── requirements.txt
```