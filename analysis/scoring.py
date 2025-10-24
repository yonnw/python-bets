"""
Sistema de scoring para avaliar probabilidade de golo na 1ª parte E Over 1.5 FT
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
        
        # Score = Percentagem de jogos com golo na 1ª parte (qualquer equipa)
        fh_percentage = h2h_stats.get('first_half_goal_percentage', 0)
        
        score = fh_percentage
        
        # Penalização se houver poucos jogos
        if total_matches < 3:
            score *= 0.7  # Reduz 30% pela falta de dados
        
        explanation = (
            f"Nos últimos {total_matches} confrontos: "
            f"{h2h_stats['matches_with_first_half_goal']} jogos com golo na 1ª parte "
            f"({fh_percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    def calculate_h2h_score_over15(self, h2h_stats: Dict) -> Tuple[float, str]:
        """
        Calcular score baseado nos confrontos diretos (OVER 1.5 FT)
        
        Args:
            h2h_stats: Estatísticas dos confrontos diretos
        
        Returns:
            Tuple com (score 0-100, explicação)
        """
        total_matches = h2h_stats.get('total_matches', 0)
        
        if total_matches == 0:
            return 0, "Sem histórico de confrontos diretos"
        
        # Score = Percentagem de jogos com Over 1.5 FT (2+ golos)
        over15_percentage = h2h_stats.get('over15_percentage', 0)
        
        score = over15_percentage
        
        # Penalização se houver poucos jogos
        if total_matches < 3:
            score *= 0.7  # Reduz 30% pela falta de dados
        
        explanation = (
            f"Nos últimos {total_matches} confrontos: "
            f"{h2h_stats.get('matches_over15', 0)} jogos com Over 1.5 FT "
            f"({over15_percentage:.1f}%)"
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
        fh_percentage = team_stats.get('first_half_goal_percentage', 0)
        
        score = fh_percentage
        
        # Penalização se houver poucos jogos
        if games_played < 5:
            score *= 0.8
        
        location = "casa" if is_home else "fora"
        explanation = (
            f"Últimos {games_played} jogos: "
            f"{team_stats['games_with_first_half_goal']} com golo na 1ª parte "
            f"({fh_percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    def calculate_team_form_score_over15(self, team_stats: Dict, is_home: bool = True) -> Tuple[float, str]:
        """
        Calcular score baseado na forma recente (OVER 1.5 FT)
        
        Args:
            team_stats: Estatísticas da equipa
            is_home: Se é a equipa da casa
        
        Returns:
            Tuple com (score 0-100, explicação)
        """
        games_played = team_stats.get('games_played', 0)
        
        if games_played == 0:
            return 0, "Sem dados de forma recente"
        
        # Score = Percentagem de jogos com Over 1.5 FT
        over15_percentage = team_stats.get('over15_percentage', 0)
        
        score = over15_percentage
        
        # Penalização se houver poucos jogos
        if games_played < 5:
            score *= 0.8
        
        location = "casa" if is_home else "fora"
        explanation = (
            f"Últimos {games_played} jogos: "
            f"{team_stats.get('games_over15', 0)} com Over 1.5 FT "
            f"({over15_percentage:.1f}%)"
        )
        
        return round(score, 2), explanation
    
    def calculate_combined_score(self, h2h_score: float, home_form_score: float,
                                away_form_score: float) -> Tuple[float, str, str]:
        """
        Calcular score final combinado
        
        Args:
            h2h_score: Score dos confrontos diretos
            home_form_score: Score da forma da equipa da casa
            away_form_score: Score da forma da equipa visitante
        
        Returns:
            Tuple com (score final 0-100, nível de confiança, recomendação)
        """
        # Score ponderado
        final_score = (
            h2h_score * self.weights['direct_confrontations'] +
            home_form_score * self.weights['home_team_form'] +
            away_form_score * self.weights['away_team_form']
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
    
    def analyze_match(self, analysis_data: Dict) -> Dict:
        """
        Analisar um jogo completo e gerar scores (Over 0.5 HT e Over 1.5 FT)
        
        Args:
            analysis_data: Dados de análise do jogo
        
        Returns:
            Dicionário com análise completa e recomendação
        """
        # ========== OVER 0.5 HT ==========
        # Calcular scores individuais Over 0.5 HT
        h2h_score, h2h_explanation = self.calculate_h2h_score(
            analysis_data['h2h']['stats']
        )
        
        home_score, home_explanation = self.calculate_team_form_score(
            analysis_data['home_team']['stats'],
            is_home=True
        )
        
        away_score, away_explanation = self.calculate_team_form_score(
            analysis_data['away_team']['stats'],
            is_home=False
        )
        
        # Score final Over 0.5 HT
        final_score, confidence, recommendation = self.calculate_combined_score(
            h2h_score, home_score, away_score
        )
        
        # ========== OVER 1.5 FT ==========
        # Calcular scores individuais Over 1.5 FT
        h2h_score_o15, h2h_explanation_o15 = self.calculate_h2h_score_over15(
            analysis_data['h2h']['stats']
        )
        
        home_score_o15, home_explanation_o15 = self.calculate_team_form_score_over15(
            analysis_data['home_team']['stats'],
            is_home=True
        )
        
        away_score_o15, away_explanation_o15 = self.calculate_team_form_score_over15(
            analysis_data['away_team']['stats'],
            is_home=False
        )
        
        # Score final Over 1.5 FT
        final_score_o15, confidence_o15, recommendation_o15 = self.calculate_combined_score(
            h2h_score_o15, home_score_o15, away_score_o15
        )
        
        # Construir explicação completa
        reasoning = self._build_reasoning(
            h2h_explanation, home_explanation, away_explanation,
            h2h_score, home_score, away_score, final_score,
            h2h_explanation_o15, home_explanation_o15, away_explanation_o15,
            h2h_score_o15, home_score_o15, away_score_o15, final_score_o15
        )
        
        return {
            # Over 0.5 HT
            'overall_score': final_score,
            'confidence_level': confidence,
            'recommendation': recommendation,
            'h2h_score': h2h_score,
            'home_form_score': home_score,
            'away_form_score': away_score,
            
            # Over 1.5 FT
            'overall_score_o15': final_score_o15,
            'confidence_level_o15': confidence_o15,
            'recommendation_o15': recommendation_o15,
            'h2h_score_o15': h2h_score_o15,
            'home_form_score_o15': home_score_o15,
            'away_form_score_o15': away_score_o15,
            
            'reasoning': reasoning,
            'details': {
                'h2h': h2h_explanation,
                'home': home_explanation,
                'away': away_explanation,
                'h2h_o15': h2h_explanation_o15,
                'home_o15': home_explanation_o15,
                'away_o15': away_explanation_o15
            }
        }
    
    def _build_reasoning(self, h2h_exp: str, home_exp: str, away_exp: str,
                        h2h_score: float, home_score: float, away_score: float,
                        final_score: float,
                        h2h_exp_o15: str, home_exp_o15: str, away_exp_o15: str,
                        h2h_score_o15: float, home_score_o15: float, away_score_o15: float,
                        final_score_o15: float) -> str:
        """Construir explicação detalhada da análise"""
        
        reasoning_parts = [
            "="*80,
            "📊 ANÁLISE OVER 0.5 HT (Golo na 1ª Parte)",
            "="*80,
            f"\n🎯 SCORE FINAL: {final_score}/100\n",
            f"\n🤝 CONFRONTOS DIRETOS (Score: {h2h_score}/100 - Peso: {self.weights['direct_confrontations']*100}%)",
            f"{h2h_exp}",
            f"\n🏠 EQUIPA DA CASA (Score: {home_score}/100 - Peso: {self.weights['home_team_form']*100}%)",
            f"{home_exp}",
            f"\n✈️ EQUIPA VISITANTE (Score: {away_score}/100 - Peso: {self.weights['away_team_form']*100}%)",
            f"{away_exp}",
            "\n" + "="*80,
            "📊 ANÁLISE OVER 1.5 FT (2+ Golos no Jogo)",
            "="*80,
            f"\n🎯 SCORE FINAL: {final_score_o15}/100\n",
            f"\n🤝 CONFRONTOS DIRETOS (Score: {h2h_score_o15}/100 - Peso: {self.weights['direct_confrontations']*100}%)",
            f"{h2h_exp_o15}",
            f"\n🏠 EQUIPA DA CASA (Score: {home_score_o15}/100 - Peso: {self.weights['home_team_form']*100}%)",
            f"{home_exp_o15}",
            f"\n✈️ EQUIPA VISITANTE (Score: {away_score_o15}/100 - Peso: {self.weights['away_team_form']*100}%)",
            f"{away_exp_o15}",
        ]
        
        # Adicionar conclusão Over 0.5 HT
        reasoning_parts.append("\n" + "="*80)
        reasoning_parts.append("✅ CONCLUSÃO OVER 0.5 HT:")
        if final_score >= 75:
            reasoning_parts.append(
                "Forte indicação de que haverá golo na 1ª parte. "
                "Ambas as equipas mostram tendência consistente de marcar/sofrer cedo."
            )
        elif final_score >= 60:
            reasoning_parts.append(
                "Probabilidade moderada de golo na 1ª parte. "
                "Há indicadores positivos mas também alguma incerteza."
            )
        elif final_score >= 45:
            reasoning_parts.append(
                "Probabilidade baixa-moderada. "
                "Considerar outros fatores antes de decidir."
            )
        else:
            reasoning_parts.append(
                "Baixa probabilidade de golo na 1ª parte "
                "com base nos dados históricos."
            )
        
        # Adicionar conclusão Over 1.5 FT
        reasoning_parts.append("\n✅ CONCLUSÃO OVER 1.5 FT:")
        if final_score_o15 >= 75:
            reasoning_parts.append(
                "Forte indicação de que haverá 2+ golos no jogo. "
                "Histórico mostra jogos com muitos golos entre estas equipas."
            )
        elif final_score_o15 >= 60:
            reasoning_parts.append(
                "Probabilidade moderada de Over 1.5 FT. "
                "Há bons indicadores mas com alguma variação."
            )
        elif final_score_o15 >= 45:
            reasoning_parts.append(
                "Probabilidade baixa-moderada de Over 1.5 FT. "
                "Analisar outros fatores antes de apostar."
            )
        else:
            reasoning_parts.append(
                "Baixa probabilidade de Over 1.5 FT "
                "baseado no histórico recente."
            )
        
        reasoning_parts.append("="*80)
        
        return "\n".join(reasoning_parts)
    
    def format_h2h_visualization(self, h2h_matches: List, 
                                 home_team_name: str, away_team_name: str) -> str:
        """
        Formatar visualização dos confrontos diretos
        
        Args:
            h2h_matches: Lista de jogos H2H
            home_team_name: Nome da equipa da casa
            away_team_name: Nome da equipa visitante
        
        Returns:
            String formatada com histórico visual
        """
        if not h2h_matches:
            return "\n   ⚠️ Sem histórico de confrontos diretos no campeonato\n"
        
        viz = f"\n   {'='*70}\n"
        viz += f"   📊 HISTÓRICO DE CONFRONTOS DIRETOS (Últimos 3 anos - Apenas jogos finalizados)\n"
        viz += f"   {'='*70}\n\n"
        
        count = 0
        for match in h2h_matches:
            # FILTRAR APENAS JOGOS FINALIZADOS
            if match.get('status') != 'FT':
                continue
                
            count += 1
            if count > 10:  # Mostrar máximo 10 jogos
                break
            
            date = match.get('date', 'Data desconhecida')
            if isinstance(date, str):
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            
            home_ht = match.get('home_goals_halftime', 0) or 0
            away_ht = match.get('away_goals_halftime', 0) or 0
            home_ft = match.get('home_goals_fulltime', 0) or 0
            away_ft = match.get('away_goals_fulltime', 0) or 0
            
            home_name = match.get('home_team_name', 'Casa')
            away_name = match.get('away_team_name', 'Fora')
            
            # Indicadores
            first_half_goal = "🟢" if (home_ht + away_ht) > 0 else "🔴"
            over15_ft = "🟢" if (home_ft + away_ft) >= 2 else "🔴"
            
            viz += f"   {count}. {date} - Over 0.5 HT: {first_half_goal} | Over 1.5 FT: {over15_ft}\n"
            viz += f"      {home_name} {home_ft} - {away_ft} {away_name}\n"
            viz += f"      1ª Parte: {home_ht}-{away_ht} | 2ª Parte: {home_ft-home_ht}-{away_ft-away_ht}\n\n"
        
        if count == 0:
            return "\n   ⚠️ Sem jogos finalizados no histórico de confrontos diretos\n"
        
        # Calcular estatísticas apenas de jogos finalizados
        finished_matches = [m for m in h2h_matches if m.get('status') == 'FT']
        total_games = len(finished_matches)
        
        games_with_fh_goal = sum(1 for m in finished_matches 
                                 if (m.get('home_goals_halftime', 0) or 0) + 
                                    (m.get('away_goals_halftime', 0) or 0) > 0)
        
        games_over15 = sum(1 for m in finished_matches 
                          if (m.get('home_goals_fulltime', 0) or 0) + 
                             (m.get('away_goals_fulltime', 0) or 0) >= 2)
        
        percentage_ht = (games_with_fh_goal / total_games * 100) if total_games > 0 else 0
        percentage_o15 = (games_over15 / total_games * 100) if total_games > 0 else 0
        
        viz += f"   {'='*70}\n"
        viz += f"   📈 RESUMO:\n"
        viz += f"   • Over 0.5 HT: {games_with_fh_goal}/{total_games} jogos ({percentage_ht:.1f}%)\n"
        viz += f"   • Over 1.5 FT: {games_over15}/{total_games} jogos ({percentage_o15:.1f}%)\n"
        viz += f"   {'='*70}\n"
        
        return viz
    
    def format_team_form_visualization(self, team_matches: List, team_name: str, 
                                   team_id: int, is_home: bool = True) -> str:
        """
        Formatar visualização da forma recente de uma equipa
        
        Args:
            team_matches: Lista de jogos da equipa
            team_name: Nome da equipa
            team_id: ID da equipa
            is_home: Se é análise da equipa da casa
        
        Returns:
            String formatada com histórico visual
        """
        if not team_matches:
            return f"\n   ⚠️ Sem histórico de jogos para {team_name}\n"
        
        location_emoji = "🏠" if is_home else "✈️"
        viz = f"\n   {'='*70}\n"
        viz += f"   {location_emoji} FORMA RECENTE - {team_name.upper()} (Últimos 10 jogos finalizados)\n"
        viz += f"   {'='*70}\n\n"
        
        count = 0
        total_fh_goals_scored = 0
        total_fh_goals_conceded = 0
        games_with_fh_goal = 0
        games_over15 = 0
        
        for match in team_matches:
            # FILTRAR APENAS JOGOS FINALIZADOS
            if match.get('status') != 'FT':
                continue
                
            count += 1
            if count > 10:  # Mostrar máximo 10 jogos
                break
            
            date = match.get('date', 'Data desconhecida')
            if isinstance(date, str):
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            
            # Determinar se jogou em casa ou fora
            is_home_game = match.get('home_team_id') == team_id
            location_marker = "🏠" if is_home_game else "✈️"
            
            home_ht = match.get('home_goals_halftime', 0) or 0
            away_ht = match.get('away_goals_halftime', 0) or 0
            home_ft = match.get('home_goals_fulltime', 0) or 0
            away_ft = match.get('away_goals_fulltime', 0) or 0
            
            home_name = match.get('home_team_name', 'Casa')
            away_name = match.get('away_team_name', 'Fora')
            
            # Calcular golos marcados/sofridos pela equipa na 1ª parte
            if is_home_game:
                team_fh_goals = home_ht
                opponent_fh_goals = away_ht
            else:
                team_fh_goals = away_ht
                opponent_fh_goals = home_ht
            
            total_fh_goals_scored += team_fh_goals
            total_fh_goals_conceded += opponent_fh_goals
            
            # Indicadores
            if (home_ht + away_ht) > 0:
                first_half_goal = "🟢"
                games_with_fh_goal += 1
            else:
                first_half_goal = "🔴"
            
            if (home_ft + away_ft) >= 2:
                over15_ft = "🟢"
                games_over15 += 1
            else:
                over15_ft = "🔴"
            
            # Resultado do jogo
            if is_home_game:
                if home_ft > away_ft:
                    result = "✅ V"
                elif home_ft < away_ft:
                    result = "❌ D"
                else:
                    result = "➖ E"
            else:
                if away_ft > home_ft:
                    result = "✅ V"
                elif away_ft < home_ft:
                    result = "❌ D"
                else:
                    result = "➖ E"
            
            viz += f"   {count}. {date} {location_marker} O0.5HT:{first_half_goal} O1.5FT:{over15_ft} {result}\n"
            viz += f"      {home_name} {home_ft} - {away_ft} {away_name}\n"
            viz += f"      1ª Parte: {home_ht}-{away_ht} | 2ª Parte: {home_ft-home_ht}-{away_ft-away_ht}\n\n"
        
        if count == 0:
            return f"\n   ⚠️ Sem jogos finalizados para {team_name}\n"
        
        # Resumo estatístico
        avg_fh_goals_scored = total_fh_goals_scored / count if count > 0 else 0
        avg_fh_goals_conceded = total_fh_goals_conceded / count if count > 0 else 0
        fh_goal_percentage = (games_with_fh_goal / count * 100) if count > 0 else 0
        over15_percentage = (games_over15 / count * 100) if count > 0 else 0
        
        viz += f"   {'='*70}\n"
        viz += f"   📈 RESUMO:\n"
        viz += f"   • Over 0.5 HT: {games_with_fh_goal}/{count} jogos ({fh_goal_percentage:.1f}%)\n"
        viz += f"   • Over 1.5 FT: {games_over15}/{count} jogos ({over15_percentage:.1f}%)\n"
        viz += f"   • Média de golos marcados na 1ª parte: {avg_fh_goals_scored:.2f}\n"
        viz += f"   • Média de golos sofridos na 1ª parte: {avg_fh_goals_conceded:.2f}\n"
        viz += f"   {'='*70}\n"
        
        return viz

if __name__ == "__main__":
    # Teste do sistema de scoring
    scoring = ScoringSystem()
    
    # Dados de exemplo
    test_data = {
        'h2h': {
            'stats': {
                'total_matches': 5,
                'matches_with_first_half_goal': 4,
                'first_half_goal_percentage': 80,
                'avg_first_half_goals': 1.4,
                'matches_over15': 4,
                'over15_percentage': 80
            }
        },
        'home_team': {
            'stats': {
                'games_played': 10,
                'games_with_first_half_goal': 7,
                'first_half_goal_percentage': 70,
                'avg_goals_first_half': 0.9,
                'games_over15': 6,
                'over15_percentage': 60
            }
        },
        'away_team': {
            'stats': {
                'games_played': 10,
                'games_with_first_half_goal': 6,
                'first_half_goal_percentage': 60,
                'avg_goals_first_half': 0.7,
                'games_over15': 7,
                'over15_percentage': 70
            }
        }
    }
    
    result = scoring.analyze_match(test_data)
    print("🧪 Teste do Sistema de Scoring:\n")
    print(f"Score Over 0.5 HT: {result['overall_score']}/100")
    print(f"Score Over 1.5 FT: {result['overall_score_o15']}/100")
    print(f"Confiança Over 0.5 HT: {result['confidence_level']}")
    print(f"Confiança Over 1.5 FT: {result['confidence_level_o15']}")
    print(f"\n{result['reasoning']}")