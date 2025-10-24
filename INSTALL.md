# 🚀 Guia de Instalação e Uso - Football Betting AI

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Chave da API Football (Plano PRO)
- Terminal/Prompt de comando

## 🔧 Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione a sua chave da API:

```
API_FOOTBALL_KEY=sua_chave_aqui
```

**Alternativa:** Você também pode editar diretamente o arquivo `config/config.py` e substituir `YOUR_API_KEY_HERE` pela sua chave.

### 3. Inicializar a base de dados

A base de dados será criada automaticamente na primeira execução.

## 🎮 Como Usar

### Executar a aplicação

```bash
python main.py
```

### Menu Principal

A aplicação apresenta um menu interativo com as seguintes opções:

1. **Analisar jogos de hoje (todas as ligas)**
   - Analisa todos os jogos de hoje das 6 ligas configuradas
   - Apresenta recomendações ordenadas por score

2. **Analisar liga específica**
   - Escolhe uma liga específica para análise
   - Útil para focar numa competição

3. **Ver previsões guardadas de hoje**
   - Mostra análises já realizadas e guardadas na BD
   - Não consome créditos da API

4. **Verificar status da API**
   - Mostra quantos requests foram usados
   - Verifica limites do plano

5. **Sair**
   - Encerra a aplicação

## 📊 Como Interpretar os Resultados

### Scores

- **75-100**: 🟢 Alta probabilidade - Recomendação: SIM
- **60-74**: 🟡 Média probabilidade - Recomendação: TALVEZ
- **45-59**: 🟡 Baixa-média probabilidade - Recomendação: TALVEZ
- **0-44**: 🔴 Baixa probabilidade - Recomendação: NÃO

### Níveis de Confiança

- **ALTA**: Dados históricos muito consistentes
- **MÉDIA**: Bons indicadores mas alguma variação
- **BAIXA**: Indicadores mistos
- **MUITO BAIXA**: Poucos dados ou indicadores negativos

### Componentes do Score

O score final é calculado com base em:

1. **Confrontos Diretos (30%)**: Últimos 5 jogos entre as equipas
2. **Forma Equipa Casa (25%)**: Últimos 10 jogos da equipa da casa
3. **Forma Equipa Visitante (25%)**: Últimos 10 jogos da equipa visitante
4. **Estatísticas 1ª Parte (20%)**: Para implementação futura

## 🔍 Exemplos de Uso

### Exemplo 1: Análise Rápida de Hoje

```bash
python main.py
# Escolher opção 1
# Ver jogos recomendados ordenados por score
```

### Exemplo 2: Focar na Premier League

```bash
python main.py
# Escolher opção 2
# Selecionar Premier League
# Ver análise detalhada dos jogos
```

### Exemplo 3: Ver Análises Anteriores

```bash
python main.py
# Escolher opção 3
# Ver previsões já calculadas (sem gastar API requests)
```

## 📁 Estrutura de Ficheiros

```
football_betting_ai/
├── config/
│   └── config.py              # Configurações gerais
├── database/
│   ├── models.py              # Modelos de dados
│   ├── db_manager.py          # Gestor da BD
│   └── football_betting.db    # Base de dados SQLite (criada automaticamente)
├── api/
│   └── api_client.py          # Cliente da API Football
├── analysis/
│   ├── data_processor.py      # Processamento de dados
│   └── scoring.py             # Sistema de pontuação
├── main.py                    # Aplicação principal
├── requirements.txt           # Dependências Python
├── .env                       # Configurações sensíveis (API key)
└── README.md                  # Documentação
```

## ⚙️ Configurações Avançadas

### Ajustar Parâmetros de Análise

Edite `config/config.py`:

```python
ANALYSIS_PARAMS = {
    'direct_confrontations': 5,  # Número de confrontos diretos
    'recent_form_games': 10,     # Jogos de forma recente
    'min_games_for_analysis': 3, # Mínimo de jogos para análise válida
}
```

### Ajustar Pesos do Score

```python
SCORING_WEIGHTS = {
    'direct_confrontations': 0.30,  # 30%
    'home_team_form': 0.25,         # 25%
    'away_team_form': 0.25,         # 25%
    'first_half_stats': 0.20,       # 20%
}
```

### Ajustar Thresholds de Confiança

```python
ALERT_THRESHOLDS = {
    'high_confidence': 0.75,    # 75%
    'medium_confidence': 0.60,  # 60%
    'low_confidence': 0.45,     # 45%
}
```

## 🔄 Adicionar Novas Ligas

Edite `config/config.py` e adicione ao dicionário `LEAGUES`:

```python
LEAGUES = {
    'Premier League': 39,
    'La Liga': 140,
    'Bundesliga': 78,
    'Serie A': 135,
    'Ligue 1': 61,
    'Primeira Liga': 94,
    'Eredivisie': 88,  # Exemplo de nova liga
}
```

## 📝 Notas Importantes

1. **Rate Limiting**: O Plano PRO permite 300 requests/minuto e 10,000/dia
2. **Cache**: Os dados são guardados na BD para evitar requests repetidos
3. **Histórico**: A aplicação acumula dados ao longo do tempo para melhorar análises
4. **Jogos Finalizados**: Apenas jogos finalizados (status 'FT') são considerados para estatísticas

## 🐛 Troubleshooting

### Erro: "API retornou erros"
- Verifique se a API key está correta
- Confirme que ainda tem requests disponíveis

### Erro: "Poucos confrontos diretos na BD"
- Normal na primeira execução
- A aplicação irá buscar dados da API automaticamente

### Base de dados vazia
- Execute a análise uma vez para popular a BD
- Os dados ficam guardados para análises futuras

## 📞 Suporte

Para mais informações sobre a API Football:
- Documentação: https://www.api-football.com/documentation-v3
- Dashboard: https://dashboard.api-football.com/

## 🚀 Próximos Passos

1. ✅ Sistema básico de análise (completo)
2. 🔄 Implementar machine learning para melhorar previsões
3. 🔄 Adicionar mais estatísticas da API
4. 🔄 Interface web
5. 🔄 Notificações automáticas
6. 🔄 Análise de odds e ROI