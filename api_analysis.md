# 📊 Análise Detalhada da API Football

## 🎯 Objetivo
Identificar os endpoints e estatísticas mais relevantes para melhorar as previsões de **Over 0.5 HT** e **Over 1.5 FT**.

---

## 🔍 Endpoints Disponíveis

### 1. **Fixtures** ⭐⭐⭐⭐⭐
**Endpoint:** `/fixtures`

**O que temos:**
- Informações básicas dos jogos
- Resultado final e halftime
- Status do jogo

**O que podemos adicionar:**
```python
# Parâmetros úteis que ainda não usamos:
- timezone: Para horários corretos
- venue: Informações do estádio
- referee: Informações do árbitro
```

**Relevância:** CRÍTICA - Base de tudo

---

### 2. **Fixtures Statistics** ⭐⭐⭐⭐⭐
**Endpoint:** `/fixtures/statistics`

**Estatísticas disponíveis que podemos usar:**

#### 🎯 Altamente Relevantes para Over 0.5 HT:
- `Shots on Goal` - Remates à baliza (indicador de pressão ofensiva)
- `Shots insidebox` - Remates dentro da área (mais perigosos)
- `Corner Kicks` - Cantos (indicam domínio e chances)
- `Ball Possession` - Posse de bola (correlação com golos)
- `Dangerous Attacks` - Ataques perigosos

#### 📈 Relevantes para Over 1.5 FT:
- `Total Shots` - Total de remates
- `Expected Goals (xG)` - Se disponível
- `Passes into final third` - Passes no último terço

**Implementação Sugerida:**
```python
def calculate_offensive_pressure_score(match_stats: Dict) -> float:
    """
    Calcular score de pressão ofensiva baseado em estatísticas
    
    Indicadores:
    - Shots on goal > 5: Ataque consistente
    - Shots insidebox > 8: Finalizações perigosas
    - Corner kicks > 5: Domínio territorial
    - Possession > 55%: Controlo do jogo
    
    Returns:
        Score 0-100
    """
    score = 0
    
    # Shots on goal (peso: 30%)
    shots_on_goal = match_stats.get('shots_on_goal', 0)
    if shots_on_goal >= 5:
        score += 30
    elif shots_on_goal >= 3:
        score += 20
    elif shots_on_goal >= 1:
        score += 10
    
    # Shots insidebox (peso: 25%)
    shots_inside = match_stats.get('shots_insidebox', 0)
    if shots_inside >= 8:
        score += 25
    elif shots_inside >= 5:
        score += 15
    elif shots_inside >= 3:
        score += 8
    
    # Corner kicks (peso: 20%)
    corners = match_stats.get('corner_kicks', 0)
    if corners >= 5:
        score += 20
    elif corners >= 3:
        score += 12
    elif corners >= 1:
        score += 5
    
    # Ball possession (peso: 15%)
    possession = match_stats.get('ball_possession', '50%')
    possession_value = float(possession.rstrip('%'))
    if possession_value >= 60:
        score += 15
    elif possession_value >= 50:
        score += 8
    
    # Dangerous attacks (peso: 10%)
    # Se disponível
    
    return min(score, 100)
```

---

### 3. **Teams Statistics** ⭐⭐⭐⭐
**Endpoint:** `/teams/statistics`

**Estatísticas da temporada por equipa:**

#### 🏠 Casa vs ✈️ Fora (Separado!)
```json
{
  "fixtures": {
    "played": {"home": 10, "away": 10},
    "wins": {"home": 6, "away": 3},
    "draws": {"home": 2, "away": 4},
    "loses": {"home": 2, "away": 3}
  },
  "goals": {
    "for": {
      "total": {"home": 20, "away": 12},
      "average": {"home": "2.0", "away": "1.2"},
      "minute": {
        "0-15": {"total": 5, "percentage": "15%"},
        "16-30": {"total": 8, "percentage": "24%"},
        "31-45": {"total": 6, "percentage": "18%"},
        ...
      }
    }
  },
  "biggest": {
    "streak": {"wins": 3},
    "wins": {"home": "4-0", "away": "2-0"},
    "loses": {"home": "0-3", "away": "0-4"}
  },
  "clean_sheet": {"home": 4, "away": 2},
  "failed_to_score": {"home": 1, "away": 4}
}
```

**Métricas Cruciais:**
1. **Golos por minuto** - MUITO IMPORTANTE
   - `0-15`, `16-30`, `31-45` = Primeira parte
   - Se > 40% dos golos são na 1ª parte = Forte indicador

2. **Average goals home/away**
   - Equipas que marcam muito em casa
   - Equipas que marcam fora

3. **Failed to score**
   - Quantas vezes não marcou
   - Importante para avaliar consistência

**Implementação Sugerida:**
```python
def get_first_half_tendency(team_stats: Dict) -> float:
    """
    Calcular tendência de golos na primeira parte
    
    Returns:
        Percentagem de golos marcados na 1ª parte (0-100)
    """
    minutes = team_stats['goals']['for']['minute']
    
    # Somar golos dos primeiros 45 minutos
    first_half_goals = 0
    total_goals = 0
    
    for period, data in minutes.items():
        goals = data.get('total', 0)
        total_goals += goals
        
        # Extrair minutos
        if '-' in period:
            start, end = period.split('-')
            if int(end) <= 45:
                first_half_goals += goals
    
    if total_goals == 0:
        return 0
    
    return (first_half_goals / total_goals) * 100
```

---

### 4. **Fixtures Events** ⭐⭐⭐
**Endpoint:** `/fixtures/events`

**Eventos do jogo:**
- Goals (com minuto exato!)
- Cards
- Substitutions

**Uso:** Validação pós-jogo
```python
def validate_prediction(match_id: int, our_prediction: Dict):
    """
    Validar se acertamos a previsão
    """
    events = api.get_fixture_events(match_id)
    
    # Verificar golos na 1ª parte
    first_half_goals = [
        e for e in events 
        if e['type'] == 'Goal' and e['time']['elapsed'] <= 45
    ]
    
    predicted_over_05_ht = our_prediction['recommendation'] == 'SIM'
    actual_over_05_ht = len(first_half_goals) > 0
    
    return predicted_over_05_ht == actual_over_05_ht
```

---

### 5. **Standings** ⭐⭐⭐
**Endpoint:** `/standings`

**Classificação da liga:**
- Posição na tabela
- Forma recente (últimos 5 jogos)
- Golos marcados/sofridos casa/fora

**Relevância:**
- Equipas no top 4 tendem a marcar mais
- Equipas em zona de despromoção podem ter jogos mais fechados

---

### 6. **Predictions** ⭐⭐⭐⭐
**Endpoint:** `/predictions`

**A própria API tem previsões!**
```json
{
  "predictions": {
    "winner": {"id": 42, "name": "Arsenal"},
    "win_or_draw": true,
    "under_over": "Over 2.5",
    "goals": {"home": "2.5", "away": "1.5"},
    "advice": "Combo Double Chance : Arsenal or draw and Over 2.5"
  },
  "comparison": {
    "form": {"home": "80%", "away": "60%"},
    "att": {"home": "85%", "away": "70%"},
    "def": {"home": "75%", "away": "65%"},
    "poisson_distribution": {"home": "45%", "away": "30%", "draw": "25%"},
    "h2h": {"home": "50%", "away": "30%", "draw": "20%"}
  }
}
```

**Podemos usar:**
- Form comparison (já implementamos manualmente)
- ATT/DEF comparison
- Poisson distribution para probabilidades

---

## 🎯 Plano de Implementação

### Fase 1: Estatísticas de Jogo (Alta Prioridade) ✅
```python
# Adicionar ao DataProcessor:
def fetch_match_statistics(self, match_id: int) -> Dict:
    """Buscar estatísticas detalhadas do jogo"""
    return self.api.get_fixture_statistics(match_id)

def calculate_offensive_metrics(self, team_id: int, league_id: int) -> Dict:
    """
    Calcular métricas ofensivas baseadas em estatísticas reais:
    - Média de shots on goal por jogo
    - Média de corner kicks
    - Posse de bola média
    - etc.
    """
```

### Fase 2: Análise de Minutos (Alta Prioridade) ⭐
```python
def get_goals_by_minute_distribution(self, team_id: int) -> Dict:
    """
    Obter distribuição de golos por período de 15 minutos
    
    Returns:
        {
            '0-15': {'percentage': 15, 'total': 5},
            '16-30': {'percentage': 20, 'total': 7},
            '31-45': {'percentage': 18, 'total': 6},
            ...
        }
    """
```

### Fase 3: Previsões da API (Média Prioridade)
```python
def get_api_predictions(self, match_id: int) -> Dict:
    """Obter previsões da própria API para comparação"""
    return self.api.get_predictions(match_id)

def compare_with_api_predictions(self, our_score: float, api_pred: Dict) -> Dict:
    """Comparar nossas previsões com as da API"""
```

### Fase 4: Validação de Resultados (Alta Prioridade) ✅
```python
def track_prediction_accuracy(self, prediction_id: int):
    """
    Verificar se a previsão estava correta após o jogo
    Atualizar base de dados com resultado real
    """
```

---

## 📊 Novo Sistema de Scoring (Proposta)

### Score Composto:
```python
FINAL_SCORE = (
    H2H_SCORE * 0.25 +                    # 25% - Confrontos diretos
    HOME_FORM_SCORE * 0.20 +              # 20% - Forma casa
    AWAY_FORM_SCORE * 0.20 +              # 20% - Forma fora
    OFFENSIVE_PRESSURE_SCORE * 0.20 +     # 20% - Pressão ofensiva (NOVO)
    MINUTE_DISTRIBUTION_SCORE * 0.15      # 15% - Tendência minutos (NOVO)
)
```

### Novos Componentes:

#### 1. **Offensive Pressure Score**
```python
# Baseado em estatísticas dos últimos 5 jogos:
- Shots on goal > 5 por jogo = +20 pontos
- Shots insidebox > 8 por jogo = +20 pontos
- Corners > 5 por jogo = +15 pontos
- Possession > 55% = +15 pontos
- Dangerous attacks (se disponível) = +15 pontos
- xG > 1.5 (se disponível) = +15 pontos
```

#### 2. **Minute Distribution Score**
```python
# Baseado na temporada completa:
- Se 40%+ dos golos são 0-45min = 100 pontos
- Se 35-40% dos golos são 0-45min = 75 pontos
- Se 30-35% dos golos são 0-45min = 50 pontos
- Se <30% dos golos são 0-45min = 25 pontos
```

---

## 🎯 Melhorias Sugeridas

### 1. **Cache Inteligente**
```python
# Cachear estatísticas da temporada (mudam pouco):
- Team statistics: 24h
- Standings: 12h
- Historical matches: permanente

# Não cachear:
- Today's fixtures: sempre atualizar
- Live statistics: sempre atualizar
```

### 2. **Pré-processamento Noturno**
```python
# Executar às 2h da manhã:
def nightly_data_update():
    """
    1. Atualizar estatísticas de todas as equipas
    2. Recalcular métricas ofensivas
    3. Atualizar distribuição de golos por minuto
    4. Preparar dados para o dia seguinte
    """
```

### 3. **Sistema de Pesos Dinâmicos**
```python
# Ajustar pesos baseado na performance:
def adjust_weights_based_on_accuracy():
    """
    Analisar últimas 100 previsões
    Ajustar pesos dos componentes
    Usar machine learning simples
    """
```

---

## 📈 Métricas de Sucesso

### Tracking:
1. **Accuracy Rate**: % de previsões corretas
2. **Precision**: Das previsões "SIM", quantas acertaram
3. **Recall**: Dos jogos com golo HT, quantos previmos
4. **F1-Score**: Média harmônica

### Objetivos:
- **Fase 1**: 60% accuracy
- **Fase 2**: 70% accuracy
- **Fase 3**: 75%+ accuracy

---

## 🚀 Próximos Passos

1. ✅ Reorganizar estrutura do projeto
2. ⏳ Implementar sistema de logging profissional
3. ⏳ Adicionar endpoints de estatísticas
4. ⏳ Implementar novos scores
5. ⏳ Sistema de validação de previsões
6. ⏳ Interface gráfica com tracking