"""
Configurações do projeto Football Betting AI
"""

import os
from datetime import datetime

# API Football Configuration
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.getenv("API_FOOTBALL_KEY", "1eea484c1c9465fbfec2497a45b26bbd")

# Ligas a analisar (apenas campeonatos internos)
LEAGUES = {
    # ALTA PROBABILIDADE DE GOLOS 1ª PARTE
    'Bundesliga': 78,           # 🇩🇪 50% Over 1.5 HT
    'Ligue 1': 61,              # 🇫🇷 43% Over 1.5 HT
    'MLS': 253,                 # 🇺🇸 3.12 golos/jogo
    'Eredivisie': 88,           # 🇳🇱 Muito ofensivo
    
    # BOA PROBABILIDADE
    'Premier League': 39,       # 🏴󠁧󠁢󠁥󠁮󠁧󠁿 56% Over 2.5
    'Primeira Liga': 94,        # 🇵🇹 Campeonato nacional
    
    # CONSIDERAR ADICIONAR
    'Saudi Pro League': 307,    # 🇸🇦 Muitos investimentos e golos
    # 'Serie A': 135,           # 🇮🇹 Mais defensivo
    # 'La Liga': 140,           # 🇪🇸 70% Over 0.5 HT (baixo)
}

# Temporada atual
CURRENT_SEASON = 2025

# Parâmetros de análise
ANALYSIS_PARAMS = {
    'direct_confrontations_years': 3,  # Confrontos diretos nos últimos 3 anos
    'recent_form_games': 10,      # Últimos 10 jogos de cada equipa
    'min_games_for_analysis': 3,  # Mínimo de jogos para análise válida
}

# Critérios de scoring
SCORING_WEIGHTS = {
    'direct_confrontations': 0.35,   # 35% peso dos confrontos diretos
    'home_team_form': 0.35,          # 35% forma da equipa da casa
    'away_team_form': 0.30,          # 30% forma da equipa visitante
    'first_half_stats': 0.00,        # 0% estatísticas específicas de 1ª parte
}

# Database
DATABASE_PATH = "football_betting.db"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = f"logs/football_betting_{datetime.now().strftime('%Y%m%d')}.log"

# API Rate Limiting (Plano PRO permite mais requests)
API_REQUESTS_PER_MINUTE = 300
API_REQUESTS_PER_DAY = 10000

# Cache settings
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 24

# Thresholds para alertas
ALERT_THRESHOLDS = {
    'high_confidence': 0.75,   # Score >= 75% = Alta confiança
    'medium_confidence': 0.60,  # Score >= 60% = Média confiança
    'low_confidence': 0.45,     # Score >= 45% = Baixa confiança
}