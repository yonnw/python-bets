"""
Configurações do projeto Football Betting AI
"""

import os
from datetime import datetime

# API Football Configuration
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.getenv("API_FOOTBALL_KEY", "1eea484c1c9465fbfec2497a45b26bbd")

# Ligas a analisar
LEAGUES = {
    'Bundesliga': 78,
    'Ligue 1': 61,
    'MLS': 253,
    'Eredivisie': 88,
    'Premier League': 39,
    'Primeira Liga': 94,
    'Saudi Pro League': 307,
}

# Temporada atual
CURRENT_SEASON = 2025

# Parâmetros de análise
ANALYSIS_PARAMS = {
    'direct_confrontations_years': 3,
    'recent_form_games': 10,
    'min_games_for_analysis': 3,
}

# Critérios de scoring
SCORING_WEIGHTS = {
    'direct_confrontations': 0.25,      # 25%
    'home_team_form': 0.20,             # 20%
    'away_team_form': 0.20,             # 20%
    'offensive_pressure': 0.20,         # 20% (NOVO)
    'minute_distribution': 0.15,        # 15% (NOVO)
}

# Database
DATABASE_PATH = "football_betting.db"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = f"logs/football_betting_{datetime.now().strftime('%Y%m%d')}.log"

# API Rate Limiting
API_REQUESTS_PER_MINUTE = 300
API_REQUESTS_PER_DAY = 10000

# Cache settings
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 24

# Thresholds para alertas
ALERT_THRESHOLDS = {
    'high_confidence': 0.75,
    'medium_confidence': 0.60,
    'low_confidence': 0.45,
}