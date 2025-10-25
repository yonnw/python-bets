"""
Interface Gráfica para Football Betting AI
Versão 1.0 - Interface básica com lista de jogos
"""

import sys
from datetime import datetime
from typing import List, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QMessageBox, QProgressBar,
    QTextEdit, QDialog, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

# Importar o sistema existente (vamos adaptar os imports depois)
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AnalysisThread(QThread):
    """Thread para executar análises sem bloquear a UI"""
    progress = pyqtSignal(int, str)  # progresso, mensagem
    finished = pyqtSignal(list)  # lista de previsões
    error = pyqtSignal(str)
    
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
    
    def run(self):
        try:
            self.progress.emit(10, "🔍 Buscando jogos de hoje...")
            
            # Aqui vamos integrar com o sistema existente
            predictions = self.app.analyze_today_matches()
            
            self.progress.emit(100, "✅ Análise concluída!")
            self.finished.emit(predictions)
            
        except Exception as e:
            self.error.emit(f"Erro: {str(e)}")


class MatchCard(QFrame):
    """Card visual para cada jogo"""
    
    def __init__(self, prediction: Dict, parent=None):
        super().__init__(parent)
        self.prediction = prediction
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Cabeçalho: Liga
        league_label = QLabel(f"🏆 {self.prediction.get('league_name', 'N/A')}")
        league_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(league_label)
        
        # Equipas
        teams_label = QLabel(
            f"⚽ {self.prediction.get('home_team', 'N/A')} vs "
            f"{self.prediction.get('away_team', 'N/A')}"
        )
        teams_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        teams_label.setWordWrap(True)
        layout.addWidget(teams_label)
        
        # Horário
        try:
            date_str = self.prediction.get('date', '')
            if date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                time_str = date_obj.strftime('%H:%M')
            else:
                time_str = "N/A"
        except:
            time_str = "N/A"
        
        time_label = QLabel(f"🕒 {time_str}")
        layout.addWidget(time_label)
        
        # Scores
        score_ht = self.prediction.get('overall_score', 0)
        score_ft = self.prediction.get('overall_score_o15', 0)
        
        # Over 0.5 HT
        emoji_ht = "🟢" if score_ht >= 75 else "🟡" if score_ht >= 60 else "🔴"
        score_ht_label = QLabel(f"{emoji_ht} Over 0.5 HT: {score_ht:.0f}/100")
        score_ht_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(score_ht_label)
        
        # Over 1.5 FT
        emoji_ft = "🟢" if score_ft >= 75 else "🟡" if score_ft >= 60 else "🔴"
        score_ft_label = QLabel(f"{emoji_ft} Over 1.5 FT: {score_ft:.0f}/100")
        score_ft_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(score_ft_label)
        
        # Recomendação
        rec_ht = self.prediction.get('recommendation', 'N/A')
        rec_ft = self.prediction.get('recommendation_o15', 'N/A')
        rec_label = QLabel(f"📊 HT: {rec_ht} | FT: {rec_ft}")
        layout.addWidget(rec_label)
        
        # Status (para tracking futuro)
        status = self.prediction.get('status', 'pending')
        if status == 'correct':
            status_label = QLabel("✅ ACERTOU")
            status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status == 'wrong':
            status_label = QLabel("❌ ERROU")
            status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            status_label = QLabel("⏳ PENDENTE")
            status_label.setStyleSheet("color: orange; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Botão Ver Detalhes
        btn_details = QPushButton("🔍 Ver Detalhes")
        btn_details.clicked.connect(self.show_details)
        layout.addWidget(btn_details)
        
        self.setLayout(layout)
        
        # Cor de fundo baseada no score
        if score_ht >= 75:
            self.setStyleSheet("QFrame { background-color: #e8f5e9; border: 2px solid #4caf50; } QLabel { color: #000000; }")
        elif score_ht >= 60:
            self.setStyleSheet("QFrame { background-color: #fff9c4; border: 2px solid #ffc107; } QLabel { color: #000000; }")
        else:
            self.setStyleSheet("QFrame { background-color: #ffebee; border: 2px solid #f44336; } QLabel { color: #000000; }")
    
    def show_details(self):
        """Mostrar diálogo com detalhes completos"""
        dialog = MatchDetailsDialog(self.prediction, self)
        dialog.exec()


class MatchDetailsDialog(QDialog):
    """Diálogo com detalhes completos do jogo"""
    
    def __init__(self, prediction: Dict, parent=None):
        super().__init__(parent)
        self.prediction = prediction
        self.setWindowTitle("Detalhes da Análise")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel(
            f"{self.prediction.get('home_team', 'N/A')} vs "
            f"{self.prediction.get('away_team', 'N/A')}"
        )
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(f"{self.prediction.get('league_name', 'N/A')}")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Criar abas para organizar informação
        from PyQt6.QtWidgets import QTabWidget
        tabs = QTabWidget()
        
        # Aba 1: Análise Geral
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout()
        
        reasoning_label = QLabel("📊 Análise Detalhada:")
        reasoning_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        analysis_layout.addWidget(reasoning_label)
        
        reasoning_text = QTextEdit()
        reasoning_text.setReadOnly(True)
        reasoning_text.setPlainText(self.prediction.get('reasoning', 'N/A'))
        reasoning_text.setFont(QFont("Courier", 9))
        analysis_layout.addWidget(reasoning_text)
        
        analysis_widget.setLayout(analysis_layout)
        tabs.addTab(analysis_widget, "📊 Análise")
        
        # Aba 2: Jogos Históricos
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        
        # Buscar jogos históricos
        history_text = self.get_match_history()
        
        history_display = QTextEdit()
        history_display.setReadOnly(True)
        history_display.setPlainText(history_text)
        history_display.setFont(QFont("Courier", 9))
        history_layout.addWidget(history_display)
        
        history_widget.setLayout(history_layout)
        tabs.addTab(history_widget, "📜 Jogos Históricos")
        
        layout.addWidget(tabs)
        
        # Botão Fechar
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
    
    def get_match_history(self) -> str:
        """Buscar e formatar histórico de jogos"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            
            home_team = self.prediction.get('home_team', '')
            away_team = self.prediction.get('away_team', '')
            
            # Buscar IDs das equipas
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM teams WHERE name = ?", (home_team,))
                home_result = cursor.fetchone()
                home_team_id = home_result['id'] if home_result else None
                
                cursor.execute("SELECT id FROM teams WHERE name = ?", (away_team,))
                away_result = cursor.fetchone()
                away_team_id = away_result['id'] if away_result else None
            
            if not home_team_id or not away_team_id:
                return "⚠️ Não foi possível encontrar IDs das equipas"
            
            output = []
            output.append("="*80)
            output.append("📜 HISTÓRICO DE JOGOS")
            output.append("="*80)
            
            # 1. Confrontos Diretos (H2H)
            output.append("\n🤝 CONFRONTOS DIRETOS\n")
            output.append("-"*80)
            
            h2h_matches = db.get_head_to_head(home_team_id, away_team_id, limit=10)
            
            if h2h_matches:
                count = 0
                for match in h2h_matches:
                    if match.get('status') != 'FT':
                        continue
                    
                    count += 1
                    if count > 10:
                        break
                    
                    date = match.get('date', 'N/A')
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
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
                    fh_goal = "🟢" if (home_ht + away_ht) > 0 else "🔴"
                    over15 = "🟢" if (home_ft + away_ft) >= 2 else "🔴"
                    
                    output.append(f"\n{count}. {date}")
                    output.append(f"   {home_name} {home_ft} - {away_ft} {away_name}")
                    output.append(f"   HT: {home_ht}-{away_ht} | 2ª Parte: {home_ft-home_ht}-{away_ft-away_ht}")
                    output.append(f"   Over 0.5 HT: {fh_goal} | Over 1.5 FT: {over15}")
            else:
                output.append("   ⚠️ Sem confrontos diretos registados")
            
            # 2. Últimos jogos da equipa da casa
            output.append("\n\n🏠 ÚLTIMOS JOGOS - " + home_team.upper())
            output.append("-"*80)
            
            home_matches = db.get_team_recent_matches(home_team_id, limit=10)
            
            if home_matches:
                count = 0
                for match in home_matches:
                    if match.get('status') != 'FT':
                        continue
                    
                    count += 1
                    if count > 10:
                        break
                    
                    date = match.get('date', 'N/A')
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
                        date = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                    
                    is_home = match.get('home_team_id') == home_team_id
                    location = "🏠" if is_home else "✈️"
                    
                    home_ht = match.get('home_goals_halftime', 0) or 0
                    away_ht = match.get('away_goals_halftime', 0) or 0
                    home_ft = match.get('home_goals_fulltime', 0) or 0
                    away_ft = match.get('away_goals_fulltime', 0) or 0
                    
                    home_name = match.get('home_team_name', 'Casa')
                    away_name = match.get('away_team_name', 'Fora')
                    
                    # Resultado
                    if is_home:
                        result = "✅" if home_ft > away_ft else "❌" if home_ft < away_ft else "➖"
                    else:
                        result = "✅" if away_ft > home_ft else "❌" if away_ft < home_ft else "➖"
                    
                    # Indicadores
                    fh_goal = "🟢" if (home_ht + away_ht) > 0 else "🔴"
                    over15 = "🟢" if (home_ft + away_ft) >= 2 else "🔴"
                    
                    output.append(f"\n{count}. {date} {location} {result}")
                    output.append(f"   {home_name} {home_ft} - {away_ft} {away_name}")
                    output.append(f"   HT: {home_ht}-{away_ht} | 2ª Parte: {home_ft-home_ht}-{away_ft-away_ht}")
                    output.append(f"   Over 0.5 HT: {fh_goal} | Over 1.5 FT: {over15}")
            else:
                output.append("   ⚠️ Sem jogos registados")
            
            # 3. Últimos jogos da equipa visitante
            output.append("\n\n✈️ ÚLTIMOS JOGOS - " + away_team.upper())
            output.append("-"*80)
            
            away_matches = db.get_team_recent_matches(away_team_id, limit=10)
            
            if away_matches:
                count = 0
                for match in away_matches:
                    if match.get('status') != 'FT':
                        continue
                    
                    count += 1
                    if count > 10:
                        break
                    
                    date = match.get('date', 'N/A')
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
                        date = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                    
                    is_home = match.get('home_team_id') == away_team_id
                    location = "🏠" if is_home else "✈️"
                    
                    home_ht = match.get('home_goals_halftime', 0) or 0
                    away_ht = match.get('away_goals_halftime', 0) or 0
                    home_ft = match.get('home_goals_fulltime', 0) or 0
                    away_ft = match.get('away_goals_fulltime', 0) or 0
                    
                    home_name = match.get('home_team_name', 'Casa')
                    away_name = match.get('away_team_name', 'Fora')
                    
                    # Resultado
                    if is_home:
                        result = "✅" if home_ft > away_ft else "❌" if home_ft < away_ft else "➖"
                    else:
                        result = "✅" if away_ft > home_ft else "❌" if away_ft < home_ft else "➖"
                    
                    # Indicadores
                    fh_goal = "🟢" if (home_ht + away_ht) > 0 else "🔴"
                    over15 = "🟢" if (home_ft + away_ft) >= 2 else "🔴"
                    
                    output.append(f"\n{count}. {date} {location} {result}")
                    output.append(f"   {home_name} {home_ft} - {away_ft} {away_name}")
                    output.append(f"   HT: {home_ht}-{away_ht} | 2ª Parte: {home_ft-home_ht}-{away_ft-away_ht}")
                    output.append(f"   Over 0.5 HT: {fh_goal} | Over 1.5 FT: {over15}")
            else:
                output.append("   ⚠️ Sem jogos registados")
            
            output.append("\n" + "="*80)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"❌ Erro ao buscar histórico: {str(e)}"


class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        self.predictions = []
        self.app_instance = None  # Vamos injetar depois
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("⚽ Football Betting AI - v2.0")
        self.setMinimumSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Mensagem de status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Área de scroll para os jogos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.matches_widget = QWidget()
        self.matches_layout = QVBoxLayout()
        self.matches_layout.setSpacing(10)
        self.matches_widget.setLayout(self.matches_layout)
        
        scroll_area.setWidget(self.matches_widget)
        main_layout.addWidget(scroll_area)
        
        central_widget.setLayout(main_layout)
        
        # Aplicar tema
        self.apply_theme()
    
    def create_header(self):
        """Criar cabeçalho com botões"""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        
        # Título
        title = QLabel("⚽ Football Betting AI")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botões
        btn_analyze = QPushButton("🔍 Analisar Jogos de Hoje")
        btn_analyze.clicked.connect(self.analyze_matches)
        btn_analyze.setMinimumHeight(40)
        btn_analyze.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        header_layout.addWidget(btn_analyze)
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.clicked.connect(self.refresh_matches)
        btn_refresh.setMinimumHeight(40)
        header_layout.addWidget(btn_refresh)
        
        btn_stats = QPushButton("📊 Estatísticas")
        btn_stats.clicked.connect(self.show_statistics)
        btn_stats.setMinimumHeight(40)
        header_layout.addWidget(btn_stats)
        
        header_widget.setLayout(header_layout)
        return header_widget
    
    def apply_theme(self):
        """Aplicar tema visual"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QTextEdit {
                background-color: white;
                color: #000000;
                border: 1px solid #cccccc;
            }
        """)
    
    def analyze_matches(self):
        """Iniciar análise de jogos"""
        if self.app_instance is None:
            QMessageBox.warning(
                self,
                "Erro",
                "Sistema ainda não foi inicializado!\n\n"
                "Por favor, aguarde..."
            )
            return
        
        # Limpar jogos anteriores
        self.clear_matches()
        
        # Mostrar progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando análise...")
        
        # Criar thread de análise
        self.analysis_thread = AnalysisThread(self.app_instance)
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.finished.connect(self.display_predictions)
        self.analysis_thread.error.connect(self.show_error)
        self.analysis_thread.start()
    
    def update_progress(self, value: int, message: str):
        """Atualizar barra de progresso"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def display_predictions(self, predictions: List[Dict]):
        """Mostrar previsões na interface"""
        self.predictions = predictions
        self.progress_bar.setVisible(False)
        
        if not predictions:
            self.status_label.setText("❌ Nenhum jogo encontrado para hoje")
            return
        
        self.status_label.setText(f"✅ {len(predictions)} jogos analisados")
        
        # Criar card para cada jogo
        for pred in predictions:
            card = MatchCard(pred)
            self.matches_layout.addWidget(card)
        
        # Spacer no final
        self.matches_layout.addStretch()
    
    def clear_matches(self):
        """Limpar todos os jogos exibidos"""
        while self.matches_layout.count():
            child = self.matches_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def refresh_matches(self):
        """Atualizar lista de jogos"""
        self.analyze_matches()
    
    def show_statistics(self):
        """Mostrar estatísticas (placeholder)"""
        QMessageBox.information(
            self,
            "Estatísticas",
            "📊 Estatísticas serão implementadas em breve!\n\n"
            "Features planejadas:\n"
            "- Accuracy geral\n"
            "- Accuracy por liga\n"
            "- Gráficos de evolução\n"
            "- ROI tracking"
        )
    
    def show_error(self, error_msg: str):
        """Mostrar erro"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ {error_msg}")
        QMessageBox.critical(self, "Erro", error_msg)
    
    def set_app_instance(self, app_instance):
        """Injetar instância do app backend"""
        self.app_instance = app_instance


def run_gui(app_instance=None):
    """
    Iniciar interface gráfica
    
    Args:
        app_instance: Instância do FootballBettingAI
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Tema moderno
    
    window = MainWindow()
    if app_instance:
        window.set_app_instance(app_instance)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # Teste standalone
    run_gui()