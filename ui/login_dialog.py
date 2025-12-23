# -*- coding: utf-8 -*-
"""
Dialogue de connexion - Design amélioré
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QComboBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from core.auth import auth_manager
from core.logger import logger
import config


class LoginDialog(QDialog):
    """Dialogue de connexion avec design moderne"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config.APP_NAME} - Connexion")
        self.setFixedSize(550, 700)  # Plus grande fenêtre
        self.setModal(True)
        
        # Centrer la fenêtre
        self.center_on_screen()
        
        # Initialiser l'UI
        self.init_ui()
        
        # Appliquer le style
        self.apply_style()
    
    def center_on_screen(self):
        """Centrer la fenêtre sur l'écran"""
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête avec gradient
        header = QFrame()
        header.setFixedHeight(200)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                border-radius: 0px;
            }
        """)
        
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(10)
        
        # Icône/Logo
        logo_label = QLabel("🏪")
        logo_label.setStyleSheet("font-size: 60px; background: transparent;")
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)
        
        # Titre
        title_label = QLabel(config.APP_NAME)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(title_label)
        
        # Sous-titre
        subtitle_label = QLabel("Système de Gestion Professionnel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px; background: transparent;")
        header_layout.addWidget(subtitle_label)
        
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Corps du formulaire
        form_container = QFrame()
        form_container.setStyleSheet("background-color: white;")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        # Message de bienvenue
        welcome_label = QLabel("Bienvenue ! Connectez-vous pour continuer")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("QLabel { color: #555; font-size: 14px; }")
        form_layout.addWidget(welcome_label)
        
        # Espacement
        form_layout.addSpacing(15)
        
        # Sélection de langue - PLUS VISIBLE
        lang_container = QFrame()
        lang_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        lang_layout = QHBoxLayout()
        lang_layout.setContentsMargins(15, 15, 15, 15)
        lang_layout.setSpacing(15)
        
        lang_icon = QLabel("🌐")
        lang_icon.setStyleSheet("font-size: 24px; background: transparent;")
        lang_layout.addWidget(lang_icon)
        
        lang_label = QLabel("Langue:")
        lang_label.setStyleSheet("color: #333; font-size: 14px; font-weight: bold; background: transparent;")
        lang_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("🇫🇷 Français", "fr")
        self.language_combo.addItem("🇩🇿 العربية", "ar")
        self.language_combo.setMinimumHeight(45)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #667eea;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                font-weight: bold;
                min-width: 180px;
            }
            QComboBox:hover {
                border-color: #764ba2;
                background-color: #f0f4ff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #667eea;
                margin-right: 10px;
            }
        """)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        
        lang_container.setLayout(lang_layout)
        form_layout.addWidget(lang_container)
        
        # Nom d'utilisateur
        username_label = QLabel("👤 Nom d'utilisateur")
        username_label.setStyleSheet("color: #333; font-size: 13px; font-weight: bold; margin-top: 10px;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.setMinimumHeight(50)
        self.username_input.returnPressed.connect(self.on_login)
        form_layout.addWidget(self.username_input)
        
        # Mot de passe
        password_label = QLabel("🔒 Mot de passe")
        password_label.setStyleSheet("color: #333; font-size: 13px; font-weight: bold; margin-top: 10px;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setMinimumHeight(50)
        self.password_input.returnPressed.connect(self.on_login)
        form_layout.addWidget(self.password_input)
        
        # Espacement
        form_layout.addSpacing(30)
        
        # Boutons avec couleurs appropriées
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Quitter")
        self.cancel_button.setMinimumHeight(55)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)
        
        self.login_button = QPushButton("Se connecter")
        self.login_button.setMinimumHeight(55)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.on_login)
        self.login_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        form_layout.addLayout(button_layout)
        
        # Espacement
        form_layout.addSpacing(20)
        
        # Info version - TRÈS VISIBLE
        version_label = QLabel(f"📱 Version {config.APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setMinimumHeight(30)
        version_label.setStyleSheet("""
            QLabel {
                color: #666; 
                font-size: 13px; 
                padding: 10px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        form_layout.addWidget(version_label)
        
        form_container.setLayout(form_layout)
        layout.addWidget(form_container)
        
        self.setLayout(layout)
        
        # Focus sur le champ username
        self.username_input.setFocus()
    
    def apply_style(self):
        """Appliquer le style CSS"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
                font-size: 15px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #999;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
        """)
        
        # Style pour le bouton Quitter (ROUGE)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Style pour le bouton Se connecter (VERT)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
    
    def on_login(self):
        """Gérer la tentative de connexion"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validation
        if not username:
            QMessageBox.warning(
                self, 
                "⚠️ Champ requis", 
                "Veuillez entrer votre nom d'utilisateur",
                QMessageBox.Ok
            )
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(
                self, 
                "⚠️ Champ requis", 
                "Veuillez entrer votre mot de passe",
                QMessageBox.Ok
            )
            self.password_input.setFocus()
            return
        
        # Désactiver le bouton pendant la connexion
        self.login_button.setEnabled(False)
        self.login_button.setText("Connexion en cours...")
        
        # Tenter la connexion
        success, message, user_data = auth_manager.login(username, password)
        
        if success:
            logger.info(f"Connexion réussie: {username}")
            self.login_successful.emit(user_data)
            self.accept()
        else:
            logger.warning(f"Échec de connexion: {username} - {message}")
            
            # Message d'erreur stylisé
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("❌ Erreur de connexion")
            error_box.setText(message)
            error_box.setInformativeText("Vérifiez vos identifiants et réessayez.")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec_()
            
            # Réactiver le bouton
            self.login_button.setEnabled(True)
            self.login_button.setText("Se connecter")
            
            # Effacer le mot de passe et refocus
            self.password_input.clear()
            self.password_input.setFocus()
    
    def get_selected_language(self):
        """Obtenir la langue sélectionnée"""
        return self.language_combo.currentData()
