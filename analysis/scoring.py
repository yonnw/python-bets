"""
Sistema de Scoring - Football Betting AI
Avalia probabilidade de Over 0.5 HT e Over 1.5 FT
Inclui métricas avançadas: Pressão Ofensiva e Distribuição de Minutos
"""

from typing import Dict, Tuple, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import SCORING_WEIGHTS, ALERT_THRESHOLDS

class ScoringSystem:
    """Sistema de pontuação para avaliar jogos"""
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
        self.thresholds = ALERT_THRESHOLDS
        print("✅ Scoring System inicializado")
    
    # ========================================================================
    # COMPONENTES DO SCORE - OVER 0.5 HT
    # ========================================================================
    
    def calculate_h2h_score(self, h2h_stats: Dict) -> Tuple[float, str]:
        """
        Calcular score baseado nos confrontos diretos (OVER 0.5 HT)
        
        Args:
            h2h_stats: Estatísticas dos confrontos diretos
        
        Returns:
            Tuple com (score 0-100, explicação)
        """
        total_matches = h2h_stats.get('total_matches', 0)
        
        if total_matches == 0:
            return 0, "Sem histórico de confrontos diretos"
        
        # Score = Percentagem de jogos com golo na 1ª parte
        matches_with_goal = h2h_stats.get('matches_with_first_half_goal', 0)
        percentage = (matches_with_goal / total_matches) * 100
        
        score = percentage
        
        # Penalização se houver poucos jogos
        if total_matches < 3:
            score *= 0.7
        
        explanation = (
            f"Nos últimos {total_matches} confrontos: "
            f"{matches_with_goal} jogos com golo na 1ª parte ({percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    def calculate_team_form_score(self, team_stats: Dict, is_home: bool = True) -> Tuple[float, str]:
        """
        Calcular score baseado na forma recente (OVER 0.5 HT)
        
        Args:
            team_stats: Estatísticas da equipa
            is_home: Se é a equipa da casa
        
        Returns:
            Tuple com (score 0-100, explicação)
        """
        games_played = team_stats.get('games_played', 0)
        
        if games_played == 0:
            return 0, "Sem dados de forma recente"
        
        # Score = Percentagem de jogos com golo na 1ª parte
        games_with_goal = team_stats.get('games_with_first_half_goal', 0)
        percentage = (games_with_goal / games_played) * 100
        
        score = percentage
        
        # Penalização se houver poucos jogos
        if games_played < 5:
            score *= 0.8
        
        location = "casa" if is_home else "fora"
        explanation = (
            f"Últimos {games_played} jogos: "
            f"{games_with_goal} com golo na 1ª parte ({percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    def calculate_offensive_pressure_score(self, pressure_data: Dict) -> Tuple[float, str]:
        """
        Calcular score baseado na pressão ofensiva
        NOVO COMPONENTE!
        
        Args:
            pressure_data: {
                'shots_on_goal_avg': float,
                'shots_insidebox_avg': float,
                'corners_avg': float,
                'possession_avg': float,
                'dangerous_attacks_avg': float
            }
        
        Returns:
            Tuple com (score 0-100, explicação)
        """
        if not pressure_data or pressure_data.get('games_count', 0) < 3:
            return 0, "Dados insuficientes para pressão ofensiva"
        
        score = 0
        details = []
        
        # 1. Shots on goal (peso 30%)
        shots = pressure_data.get('shots_on_goal_avg', 0) or 0
        if shots >= 5:
            score += 30
            details.append(f"Excelente finalização ({shots:.1f} remates à baliza/jogo)")
        elif shots >= 3:
            score += 20
            details.append(f"Boa finalização ({shots:.1f} remates/jogo)")
        elif shots >= 1:
            score += 10
            details.append(f"Finalização moderada ({shots:.1f} remates/jogo)")
        
        # 2. Shots insidebox (peso 25%)
        inside = pressure_data.get('shots_insidebox_avg', 0) or 0
        if inside >= 8:
            score += 25
            details.append(f"Muitos remates dentro da área ({inside:.1f}/jogo)")
        elif inside >= 5:
            score += 15
        elif inside >= 3:
            score += 8
        
        # 3. Corner kicks (peso 20%)
        corners = pressure_data.get('corners_avg', 0) or 0
        if corners >= 5:
            score += 20
            details.append(f"Domínio territorial ({corners:.1f} cantos/jogo)")
        elif corners >= 3:
            score += 12
        elif corners >= 1:
            score += 5
        
        # 4. Ball possession (peso 15%)
        possession = pressure_data.get('possession_avg', 0) or 0
        if possession >= 60:
            score += 15
            details.append(f"Controlo do jogo ({possession:.1f}% posse)")
        elif possession >= 50:
            score += 8
        
        # 5. Dangerous attacks (peso 10%)
        dangerous = pressure_data.get('dangerous_attacks_avg', 0) or 0
        if dangerous >= 40:
            score += 10
        elif dangerous >= 30:
            score += 6
        
        explanation = "Pressão ofensiva: " + ("; ".join(details) if details else "Moderada")
        
        return min(score, 100), explanation
    
    def calculate_minute_distribution_score(self, distribution_data: Dict) -> Tuple[float, str]:
        """
        Calcular score baseado na distribuição de golos por minuto
        NOVO COMPONENTE!
        
        Args:
            distribution_data: {
                'first_half_percentage': float,
                'total_goals': int,
                '0-15': {'count': int, 'percentage': float},
                '16-30': {'count': int, 'percentage': float},
                '31-45': {'count': int, 'percentage': float}
            }
        
        Returns:
            Tuple com (score 0-100, explicação)
        """
        if not distribution_data or distribution_data.get('total', 0) < 5:
            return 0, "Dados insuficientes para distribuição temporal"
        
        # Percentagem de golos na 1ª parte
        first_half_pct = distribution_data.get('first_half_percentage', 0)
        total_goals = distribution_data.get('total', 0)
        
        # Converter percentagem para score
        if first_half_pct >= 45:
            score = 100
            level = "Muito alta"
        elif first_half_pct >= 40:
            score = 85
            level = "Alta"
        elif first_half_pct >= 35:
            score = 70
            level = "Boa"
        elif first_half_pct >= 30:
            score = 55
            level = "Moderada"
        elif first_half_pct >= 25:
            score = 40
            level = "Baixa"
        else:
            score = 25
            level = "Muito baixa"
        
        explanation = (
            f"{level} tendência de golos na 1ª parte "
            f"({first_half_pct:.1f}% dos {total_goals} golos)"
        )
        
        return score, explanation
    
    # ========================================================================
    # COMPONENTES DO SCORE - OVER 1.5 FT
    # ========================================================================
    
    def calculate_h2h_score_over15(self, h2h_stats: Dict) -> Tuple[float, str]:
        """Calcular score H2H para Over 1.5 FT"""
        total_matches = h2h_stats.get('total_matches', 0)
        
        if total_matches == 0:
            return 0, "Sem histórico de confrontos diretos"
        
        matches_over15 = h2h_stats.get('matches_over15', 0)
        percentage = (matches_over15 / total_matches) * 100
        
        score = percentage
        
        if total_matches < 3:
            score *= 0.7
        
        explanation = (
            f"Nos últimos {total_matches} confrontos: "
            f"{matches_over15} jogos com Over 1.5 FT ({percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    def calculate_team_form_score_over15(self, team_stats: Dict, is_home: bool = True) -> Tuple[float, str]:
        """Calcular score de forma para Over 1.5 FT"""
        games_played = team_stats.get('games_played', 0)
        
        if games_played == 0:
            return 0, "Sem dados de forma recente"
        
        games_over15 = team_stats.get('games_over15', 0)
        percentage = (games_over15 / games_played) * 100
        
        score = percentage
        
        if games_played < 5:
            score *= 0.8
        
        explanation = (
            f"Últimos {games_played} jogos: "
            f"{games_over15} com Over 1.5 FT ({percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    # ========================================================================
    # SCORE FINAL COMBINADO
    # ========================================================================
    
    def calculate_combined_score(self, component_scores: Dict) -> Tuple[float, str, str]:
        """
        Calcular score final combinado com todos os componentes
        
        Args:
            component_scores: {
                'h2h': float,
                'home_form': float,
                'away_form': float,
                'offensive_pressure': float (opcional),
                'minute_distribution': float (opcional)
            }
        
        Returns:
            Tuple com (score final 0-100, nível de confiança, recomendação)
        """
        # Obter scores
        h2h = component_scores.get('h2h', 0)
        home = component_scores.get('home_form', 0)
        away = component_scores.get('away_form', 0)
        pressure = component_scores.get('offensive_pressure', 0)
        distribution = component_scores.get('minute_distribution', 0)
        
        # Calcular score ponderado
        final_score = (
            h2h * self.weights.get('direct_confrontations', 0.25) +
            home * self.weights.get('home_team_form', 0.20) +
            away * self.weights.get('away_team_form', 0.20) +
            pressure * self.weights.get('offensive_pressure', 0.20) +
            distribution * self.weights.get('minute_distribution', 0.15)
        )
        
        # Determinar nível de confiança
        if final_score >= self.thresholds['high_confidence'] * 100:
            confidence = "ALTA"
            recommendation = "SIM"
        elif final_score >= self.thresholds['medium_confidence'] * 100:
            confidence = "MÉDIA"
            recommendation = "TALVEZ"
        elif final_score >= self.thresholds['low_confidence'] * 100:
            confidence = "BAIXA"
            recommendation = "TALVEZ"
        else:
            confidence = "MUITO BAIXA"
            recommendation = "NÃO"
        
        return round(final_score, 2), confidence, recommendation
    
    # ========================================================================
    # ANÁLISE COMPLETA DE JOGO
    # ========================================================================
    
    def analyze_match(self, analysis_data: Dict) -> Dict:
        """
        Analisar um jogo completo e gerar scores
        
        Args:
            analysis_data: {
                'h2h': {'stats': {...}, 'matches': [...]},
                'home_team': {'stats': {...}, 'matches': [...]},
                'away_team': {'stats': {...}, 'matches': [...]},
                'home_pressure': {...} (opcional),
                'away_pressure': {...} (opcional),
                'home_distribution': {...} (opcional),
                'away_distribution': {...} (opcional)
            }
        
        Returns:
            Dicionário com análise completa
        """
        # ========== OVER 0.5 HT ==========
        
        # Scores individuais
        h2h_score, h2h_exp = self.calculate_h2h_score(
            analysis_data['h2h']['stats']
        )
        
        home_score, home_exp = self.calculate_team_form_score(
            analysis_data['home_team']['stats'],
            is_home=True
        )
        
        away_score, away_exp = self.calculate_team_form_score(
            analysis_data['away_team']['stats'],
            is_home=False
        )
        
        # Novos componentes (se disponíveis)
        home_pressure_score = 0
        away_pressure_score = 0
        pressure_exp = "Dados não disponíveis"
        
        if 'home_pressure' in analysis_data and 'away_pressure' in analysis_data:
            hp_score, hp_exp = self.calculate_offensive_pressure_score(
                analysis_data['home_pressure']
            )
            ap_score, ap_exp = self.calculate_offensive_pressure_score(
                analysis_data['away_pressure']
            )
            home_pressure_score = hp_score
            away_pressure_score = ap_score
            pressure_exp = f"Casa: {hp_exp} | Fora: {ap_exp}"
        
        # Média de pressão ofensiva
        avg_pressure = (home_pressure_score + away_pressure_score) / 2
        
        # Distribuição de minutos
        home_dist_score = 0
        away_dist_score = 0
        dist_exp = "Dados não disponíveis"
        
        if 'home_distribution' in analysis_data and 'away_distribution' in analysis_data:
            hd_score, hd_exp = self.calculate_minute_distribution_score(
                analysis_data['home_distribution']
            )
            ad_score, ad_exp = self.calculate_minute_distribution_score(
                analysis_data['away_distribution']
            )
            home_dist_score = hd_score
            away_dist_score = ad_score
            dist_exp = f"Casa: {hd_exp} | Fora: {ad_exp}"
        
        # Média de distribuição
        avg_distribution = (home_dist_score + away_dist_score) / 2
        
        # Score final Over 0.5 HT
        final_score, confidence, recommendation = self.calculate_combined_score({
            'h2h': h2h_score,
            'home_form': home_score,
            'away_form': away_score,
            'offensive_pressure': avg_pressure,
            'minute_distribution': avg_distribution
        })
        
        # ========== OVER 1.5 FT ==========
        
        h2h_score_o15, h2h_exp_o15 = self.calculate_h2h_score_over15(
            analysis_data['h2h']['stats']
        )
        
        home_score_o15, home_exp_o15 = self.calculate_team_form_score_over15(
            analysis_data['home_team']['stats'],
            is_home=True
        )
        
        away_score_o15, away_exp_o15 = self.calculate_team_form_score_over15(
            analysis_data['away_team']['stats'],
            is_home=False
        )
        
        # Score final Over 1.5 FT
        final_score_o15, confidence_o15, recommendation_o15 = self.calculate_combined_score({
            'h2h': h2h_score_o15,
            'home_form': home_score_o15,
            'away_form': away_score_o15,
            'offensive_pressure': avg_pressure * 0.8,  # Menos peso para FT
            'minute_distribution': 0  # Não relevante para FT
        })
        
        # Construir reasoning
        reasoning = self._build_reasoning(
            h2h_exp, home_exp, away_exp, pressure_exp, dist_exp,
            h2h_score, home_score, away_score, avg_pressure, avg_distribution,
            final_score, confidence,
            h2h_exp_o15, home_exp_o15, away_exp_o15,
            h2h_score_o15, home_score_o15, away_score_o15,
            final_score_o15, confidence_o15
        )
        
        return {
            # Over 0.5 HT
            'overall_score': final_score,
            'confidence_level': confidence,
            'recommendation': recommendation,
            'h2h_score': h2h_score,
            'home_form_score': home_score,
            'away_form_score': away_score,
            'offensive_pressure_score': avg_pressure,
            'minute_distribution_score': avg_distribution,
            
            # Over 1.5 FT
            'overall_score_o15': final_score_o15,
            'confidence_level_o15': confidence_o15,
            'recommendation_o15': recommendation_o15,
            'h2h_score_o15': h2h_score_o15,
            'home_form_score_o15': home_score_o15,
            'away_form_score_o15': away_score_o15,
            
            'reasoning': reasoning,
        }
    
    def _build_reasoning(self, h2h_exp, home_exp, away_exp, pressure_exp, dist_exp,
                        h2h_score, home_score, away_score, pressure_score, dist_score,
                        final_score, confidence,
                        h2h_exp_o15, home_exp_o15, away_exp_o15,
                        h2h_score_o15, home_score_o15, away_score_o15,
                        final_score_o15, confidence_o15) -> str:
        """Construir explicação detalhada"""
        
        parts = [
            "="*80,
            "📊 ANÁLISE OVER 0.5 HT (Golo na 1ª Parte)",
            "="*80,
            f"\n🎯 SCORE FINAL: {final_score}/100 | Confiança: {confidence}\n",
            
            f"🤝 H2H ({self.weights['direct_confrontations']*100:.0f}%): {h2h_score}/100",
            f"   {h2h_exp}",
            
            f"\n🏠 Casa ({self.weights['home_team_form']*100:.0f}%): {home_score}/100",
            f"   {home_exp}",
            
            f"\n✈️ Fora ({self.weights['away_team_form']*100:.0f}%): {away_score}/100",
            f"   {away_exp}",
            
            f"\n⚡ Pressão Ofensiva ({self.weights['offensive_pressure']*100:.0f}%): {pressure_score:.1f}/100",
            f"   {pressure_exp}",
            
            f"\n⏱️ Distribuição Temporal ({self.weights['minute_distribution']*100:.0f}%): {dist_score:.1f}/100",
            f"   {dist_exp}",
            
            "\n" + "="*80,
            "📊 ANÁLISE OVER 1.5 FT (2+ Golos no Jogo)",
            "="*80,
            f"\n🎯 SCORE FINAL: {final_score_o15}/100 | Confiança: {confidence_o15}\n",
            
            f"🤝 H2H: {h2h_score_o15}/100 | {h2h_exp_o15}",
            f"🏠 Casa: {home_score_o15}/100 | {home_exp_o15}",
            f"✈️ Fora: {away_score_o15}/100 | {away_exp_o15}",
            
            "\n" + "="*80,
        ]
        
        return "\n".join(parts)

# ============================================================================
# Teste do Scoring System
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTE DO SCORING SYSTEM")
    print("="*80 + "\n")
    
    scoring = ScoringSystem()
    
    # Dados de teste
    test_data = {
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
        'home_pressure': {
            'games_count': 10,
            'shots_on_goal_avg': 5.5,
            'shots_insidebox_avg': 8.2,
            'corners_avg': 6.1,
            'possession_avg': 58.0
        },
        'away_pressure': {
            'games_count': 10,
            'shots_on_goal_avg': 4.2,
            'shots_insidebox_avg': 6.5,
            'corners_avg': 4.8,
            'possession_avg': 52.0
        },
        'home_distribution': {
            'total': 25,
            'first_half_percentage': 42.0
        },
        'away_distribution': {
            'total': 20,
            'first_half_percentage': 38.0
        }
    }
    
    result = scoring.analyze_match(test_data)
    
    print(f"Score Over 0.5 HT: {result['overall_score']}/100")
    print(f"Confiança: {result['confidence_level']}")
    print(f"Recomendação: {result['recommendation']}")
    
    print(f"\nScore Over 1.5 FT: {result['overall_score_o15']}/100")
    print(f"Confiança: {result['confidence_level_o15']}")
    print(f"Recomendação: {result['recommendation_o15']}")
    
    print("\n" + "="*80)
    print("✅ Scoring System testado com sucesso!")
    print("="*80 + "\n")