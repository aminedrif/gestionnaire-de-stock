# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QShortcut
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt
from ui.pos_page import POSPage
from core.i18n import i18n_manager
import config

class CashierWindow(QMainWindow):
    """
    Fenêtre autonome pour le mode Caisse (Plein écran/Focus)
    Seule l'interface de vente est affichée.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mode Caisse - " + config.APP_NAME)
        self.resize(1200, 800)
        
        # Apply style
        self.apply_theme()
        
        # Init UI
        self.init_ui()
        
        # Layout direction
        if i18n_manager.is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            
        # Shortcuts
        self.create_shortcuts()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Embed POS Page
        self.pos_page = POSPage(self)
        layout.addWidget(self.pos_page)

    def apply_theme(self):
        # Ensure we have a clean white background or matching theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
        """)

    def create_shortcuts(self):
        # Escape to close? Maybe confirmation needed.
        # ESC conflict with some POS inputs? Standard is usually ESC to clear or cancel.
        # Let's use Ctrl+Q or a Close button UI if needed. 
        # Standard window close (X) handles closeEvent.
        pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Quitter Caisse", 
                                     "Voulez-vous fermer le mode caisse ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
