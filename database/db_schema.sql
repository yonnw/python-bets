-- ============================================================================
-- FOOTBALL BETTING AI - DATABASE SCHEMA
-- Objetivo: Análise Over 0.5 HT (golo na 1ª parte) e Over 1.5 FT (2+ golos)
-- ============================================================================

-- ============================================================================
-- TABELA: teams
-- Armazena informações básicas das equipas
-- ============================================================================
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT,
    country TEXT,
    founded INTEGER,
    logo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABELA: leagues
-- Armazena informações das ligas/competições
-- ============================================================================
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    country TEXT,
    logo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id)
);

-- ============================================================================
-- TABELA: seasons
-- Armazena temporadas por liga
-- ============================================================================
CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    current BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    UNIQUE(league_id, year)
);

-- ============================================================================
-- TABELA: fixtures (jogos)
-- Armazena informações básicas dos jogos
-- ============================================================================
CREATE TABLE IF NOT EXISTS fixtures (
    id INTEGER PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    round TEXT,
    date TIMESTAMP NOT NULL,
    timestamp INTEGER,
    
    -- Equipas
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    
    -- Status do jogo
    status_short TEXT,  -- NS, 1H, HT, 2H, FT, PST, CANC, etc.
    status_long TEXT,
    status_elapsed INTEGER,
    
    -- Estádio e Árbitro
    venue_id INTEGER,
    venue_name TEXT,
    venue_city TEXT,
    referee TEXT,
    
    -- Resultados
    home_goals INTEGER,
    away_goals INTEGER,
    home_goals_halftime INTEGER,
    away_goals_halftime INTEGER,
    home_goals_extratime INTEGER,
    away_goals_extratime INTEGER,
    home_goals_penalty INTEGER,
    away_goals_penalty INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);

-- ============================================================================
-- TABELA: fixture_statistics
-- Estatísticas detalhadas por equipa em cada jogo
-- CRÍTICO para análise de pressão ofensiva
-- ============================================================================
CREATE TABLE IF NOT EXISTS fixture_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    
    -- Remates (CRÍTICO para Over 0.5 HT)
    shots_on_goal INTEGER,
    shots_off_goal INTEGER,
    total_shots INTEGER,
    blocked_shots INTEGER,
    shots_insidebox INTEGER,
    shots_outsidebox INTEGER,
    
    -- Posse e Passes
    ball_possession INTEGER,  -- Percentagem
    total_passes INTEGER,
    passes_accurate INTEGER,
    passes_percentage INTEGER,
    
    -- Ataques
    attacks INTEGER,
    dangerous_attacks INTEGER,
    
    -- Cantos e Faltas
    corner_kicks INTEGER,
    offsides INTEGER,
    fouls INTEGER,
    
    -- Cartões
    yellow_cards INTEGER,
    red_cards INTEGER,
    
    -- Guarda-Redes
    goalkeeper_saves INTEGER,
    
    -- Expected Goals (se disponível)
    expected_goals REAL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(fixture_id, team_id)
);

-- ============================================================================
-- TABELA: fixture_events
-- Eventos do jogo com minuto exato
-- ESSENCIAL para análise de distribuição de golos por minuto
-- ============================================================================
CREATE TABLE IF NOT EXISTS fixture_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    
    -- Tempo
    time_elapsed INTEGER NOT NULL,
    time_extra INTEGER,
    
    -- Tipo de evento
    type TEXT NOT NULL,  -- Goal, Card, subst, Var
    detail TEXT,  -- Normal Goal, Own Goal, Penalty, Yellow Card, etc.
    
    -- Jogador
    player_id INTEGER,
    player_name TEXT,
    
    -- Assistência (para golos)
    assist_id INTEGER,
    assist_name TEXT,
    
    -- Informação adicional
    comments TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- ============================================================================
-- TABELA: team_statistics
-- Estatísticas agregadas da equipa na temporada
-- Para análise de tendências e forma
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    
    -- Jogos
    played_home INTEGER DEFAULT 0,
    played_away INTEGER DEFAULT 0,
    played_total INTEGER DEFAULT 0,
    
    wins_home INTEGER DEFAULT 0,
    wins_away INTEGER DEFAULT 0,
    wins_total INTEGER DEFAULT 0,
    
    draws_home INTEGER DEFAULT 0,
    draws_away INTEGER DEFAULT 0,
    draws_total INTEGER DEFAULT 0,
    
    loses_home INTEGER DEFAULT 0,
    loses_away INTEGER DEFAULT 0,
    loses_total INTEGER DEFAULT 0,
    
    -- Golos Marcados
    goals_for_home INTEGER DEFAULT 0,
    goals_for_away INTEGER DEFAULT 0,
    goals_for_total INTEGER DEFAULT 0,
    
    goals_for_avg_home REAL DEFAULT 0,
    goals_for_avg_away REAL DEFAULT 0,
    goals_for_avg_total REAL DEFAULT 0,
    
    -- Golos Sofridos
    goals_against_home INTEGER DEFAULT 0,
    goals_against_away INTEGER DEFAULT 0,
    goals_against_total INTEGER DEFAULT 0,
    
    goals_against_avg_home REAL DEFAULT 0,
    goals_against_avg_away REAL DEFAULT 0,
    goals_against_avg_total REAL DEFAULT 0,
    
    -- Clean Sheets
    clean_sheet_home INTEGER DEFAULT 0,
    clean_sheet_away INTEGER DEFAULT 0,
    clean_sheet_total INTEGER DEFAULT 0,
    
    -- Failed to Score
    failed_to_score_home INTEGER DEFAULT 0,
    failed_to_score_away INTEGER DEFAULT 0,
    failed_to_score_total INTEGER DEFAULT 0,
    
    -- DISTRIBUIÇÃO DE GOLOS POR MINUTO (CRÍTICO!)
    goals_minute_0_15 INTEGER DEFAULT 0,
    goals_minute_16_30 INTEGER DEFAULT 0,
    goals_minute_31_45 INTEGER DEFAULT 0,
    goals_minute_46_60 INTEGER DEFAULT 0,
    goals_minute_61_75 INTEGER DEFAULT 0,
    goals_minute_76_90 INTEGER DEFAULT 0,
    goals_minute_91_105 INTEGER DEFAULT 0,
    goals_minute_106_120 INTEGER DEFAULT 0,
    
    -- Percentagens de golos por período
    goals_minute_0_15_pct REAL DEFAULT 0,
    goals_minute_16_30_pct REAL DEFAULT 0,
    goals_minute_31_45_pct REAL DEFAULT 0,
    
    -- Forma recente (últimos 5 jogos)
    form_last_5 TEXT,  -- Ex: "WWDLW"
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    UNIQUE(team_id, league_id, season)
);

-- ============================================================================
-- TABELA: predictions
-- Nossas previsões para cada jogo
-- ============================================================================
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    
    -- Informações do jogo
    date TIMESTAMP NOT NULL,
    league_id INTEGER NOT NULL,
    league_name TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    
    -- OVER 0.5 HT (Golo na 1ª Parte)
    score_over_05_ht REAL NOT NULL,
    confidence_over_05_ht TEXT NOT NULL,
    recommendation_over_05_ht TEXT NOT NULL,
    
    -- Componentes do score Over 0.5 HT
    h2h_score REAL,
    home_form_score REAL,
    away_form_score REAL,
    offensive_pressure_score REAL,
    minute_distribution_score REAL,
    
    -- OVER 1.5 FT (2+ Golos no Jogo)
    score_over_15_ft REAL NOT NULL,
    confidence_over_15_ft TEXT NOT NULL,
    recommendation_over_15_ft TEXT NOT NULL,
    
    -- Componentes do score Over 1.5 FT
    h2h_score_o15 REAL,
    home_form_score_o15 REAL,
    away_form_score_o15 REAL,
    offensive_pressure_score_o15 REAL,
    
    -- Reasoning
    reasoning TEXT,
    
    -- Validação (após o jogo)
    actual_result_ht INTEGER,  -- 1 se houve golo HT, 0 se não
    actual_result_ft INTEGER,  -- Total de golos FT
    prediction_correct_ht BOOLEAN,
    prediction_correct_ft BOOLEAN,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,
    
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id),
    UNIQUE(fixture_id)
);

-- ============================================================================
-- TABELA: prediction_accuracy
-- Track de performance das previsões
-- ============================================================================
CREATE TABLE IF NOT EXISTS prediction_accuracy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    league_id INTEGER,
    
    -- Over 0.5 HT
    total_predictions_ht INTEGER DEFAULT 0,
    correct_predictions_ht INTEGER DEFAULT 0,
    accuracy_ht REAL DEFAULT 0,
    
    -- Over 1.5 FT
    total_predictions_ft INTEGER DEFAULT 0,
    correct_predictions_ft INTEGER DEFAULT 0,
    accuracy_ft REAL DEFAULT 0,
    
    -- Por nível de confiança
    high_confidence_accuracy_ht REAL DEFAULT 0,
    medium_confidence_accuracy_ht REAL DEFAULT 0,
    low_confidence_accuracy_ht REAL DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date, league_id)
);

-- ============================================================================
-- ÍNDICES para performance
-- ============================================================================

-- Fixtures
CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(date);
CREATE INDEX IF NOT EXISTS idx_fixtures_teams ON fixtures(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_league_season ON fixtures(league_id, season);
CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(status_short);

-- Statistics
CREATE INDEX IF NOT EXISTS idx_fixture_stats_fixture ON fixture_statistics(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_stats_team ON fixture_statistics(team_id);

-- Events
CREATE INDEX IF NOT EXISTS idx_fixture_events_fixture ON fixture_events(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_events_type ON fixture_events(type);
CREATE INDEX IF NOT EXISTS idx_fixture_events_time ON fixture_events(time_elapsed);

-- Team Statistics
CREATE INDEX IF NOT EXISTS idx_team_stats_team ON team_statistics(team_id);
CREATE INDEX IF NOT EXISTS idx_team_stats_league_season ON team_statistics(league_id, season);

-- Predictions
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(date);
CREATE INDEX IF NOT EXISTS idx_predictions_fixture ON predictions(fixture_id);
CREATE INDEX IF NOT EXISTS idx_predictions_league ON predictions(league_id);

-- ============================================================================
-- VIEWS úteis
-- ============================================================================

-- View: Jogos com estatísticas completas
CREATE VIEW IF NOT EXISTS fixtures_with_stats AS
SELECT 
    f.*,
    hs.shots_on_goal as home_shots_on_goal,
    hs.total_shots as home_total_shots,
    hs.corner_kicks as home_corners,
    hs.ball_possession as home_possession,
    as_.shots_on_goal as away_shots_on_goal,
    as_.total_shots as away_total_shots,
    as_.corner_kicks as away_corners,
    as_.ball_possession as away_possession
FROM fixtures f
LEFT JOIN fixture_statistics hs ON f.id = hs.fixture_id AND f.home_team_id = hs.team_id
LEFT JOIN fixture_statistics as_ ON f.id = as_.fixture_id AND f.away_team_id = as_.team_id;

-- View: Análise de golos por período
CREATE VIEW IF NOT EXISTS goals_by_period AS
SELECT 
    fixture_id,
    SUM(CASE WHEN time_elapsed <= 15 THEN 1 ELSE 0 END) as goals_0_15,
    SUM(CASE WHEN time_elapsed > 15 AND time_elapsed <= 30 THEN 1 ELSE 0 END) as goals_16_30,
    SUM(CASE WHEN time_elapsed > 30 AND time_elapsed <= 45 THEN 1 ELSE 0 END) as goals_31_45,
    SUM(CASE WHEN time_elapsed <= 45 THEN 1 ELSE 0 END) as goals_first_half,
    SUM(CASE WHEN time_elapsed > 45 THEN 1 ELSE 0 END) as goals_second_half,
    COUNT(*) as total_goals
FROM fixture_events
WHERE type = 'Goal' AND detail NOT IN ('Missed Penalty')
GROUP BY fixture_id;

-- ============================================================================
-- TRIGGERS para manter dados atualizados
-- ============================================================================

-- Atualizar updated_at quando fixture é modificado
CREATE TRIGGER IF NOT EXISTS update_fixture_timestamp 
AFTER UPDATE ON fixtures
BEGIN
    UPDATE fixtures SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Atualizar updated_at quando team_statistics é modificado
CREATE TRIGGER IF NOT EXISTS update_team_stats_timestamp 
AFTER UPDATE ON team_statistics
BEGIN
    UPDATE team_statistics SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;