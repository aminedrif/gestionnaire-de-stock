# -*- coding: utf-8 -*-
"""
Page d'accueil avec calculatrice et accès rapide
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QLineEdit, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime


class HomePage(QWidget):
    """Page d'accueil avec widgets utiles"""
    
    # Signaux pour la navigation et actions
    navigate_to = pyqtSignal(str) # page_name
    quick_scan = pyqtSignal(str) # barcode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # En-tête de bienvenue
        header_layout = QHBoxLayout()
        
        welcome_label = QLabel("🏪 Tableau de Bord")
        welcome_font = QFont()
        welcome_font.setPointSize(28)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #667eea;")
        header_layout.addWidget(welcome_label)
        
        header_layout.addStretch()
        
        # Date et heure
        now = datetime.now()
        date_label = QLabel(now.strftime("%A %d %B %Y"))
        date_label.setStyleSheet("color: #666; font-size: 16px;")
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # Mini Caisse (Scan rapide)
        scan_group = QGroupBox("⚡ Scan Rapide & Caisse")
        scan_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding-top: 20px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: #e74c3c;
            }
        """)
        scan_layout = QHBoxLayout()
        
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Scanner un produit ici pour l'ajouter directement au panier...")
        self.scan_input.setMinimumHeight(50)
        self.scan_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: #fff;
            }
        """)
        self.scan_input.returnPressed.connect(self.handle_scan)
        scan_layout.addWidget(self.scan_input)
        
        scan_btn = QPushButton("🛒 Ajouter")
        scan_btn.setMinimumHeight(50)
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        scan_btn.clicked.connect(self.handle_scan)
        scan_layout.addWidget(scan_btn)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Boutons d'accès rapide
        quick_access_label = QLabel("🚀 Accès Rapide")
        quick_access_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
        layout.addWidget(quick_access_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Bouton Caisse
        btn_pos = self.create_quick_button("🛒", "CAISSE", "Point de vente", "#667eea", "pos")
        buttons_layout.addWidget(btn_pos)
        
        # Bouton Produits
        btn_products = self.create_quick_button("📦", "PRODUITS", "Gestion stock", "#3498db", "products")
        buttons_layout.addWidget(btn_products)
        
        # Bouton Clients
        btn_customers = self.create_quick_button("👥", "CLIENTS", "Fidélité", "#2ecc71", "customers")
        buttons_layout.addWidget(btn_customers)
        
        # Bouton Rapports
        btn_reports = self.create_quick_button("📊", "RAPPORTS", "Statistiques", "#f39c12", "reports")
        buttons_layout.addWidget(btn_reports)
        
        layout.addLayout(buttons_layout)
        
        # Section calculatrice et infos
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Calculatrice
        calc_container = self.create_calculator()
        content_layout.addWidget(calc_container)
        
        # Statistiques rapides
        stats_container = self.create_stats_widget()
        content_layout.addWidget(stats_container)
        
        layout.addLayout(content_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def handle_scan(self):
        """Gérer le scan rapide"""
        code = self.scan_input.text().strip()
        if code:
            self.quick_scan.emit(code)
            self.scan_input.clear()
    
    def create_quick_button(self, icon, title, subtitle, color, page_target):
        """Créer un bouton d'accès rapide"""
        button = QPushButton()
        button.setMinimumSize(200, 100)
        button.setCursor(Qt.PointingHandCursor)
        
        # Layout du bouton
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(5)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; background: transparent; color: white; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 11px; background: transparent; color: rgba(255,255,255,0.8); border: none;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(subtitle_label)
        
        button.setLayout(btn_layout)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 12px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        
        button.clicked.connect(lambda: self.navigate_to.emit(page_target))
        return button
    
    def create_calculator(self):
        """Créer la calculatrice"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #e0e0e0;
            }
        """)
        # Calculatrice plus grande
        container.setMinimumWidth(400)
        container.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("🔢 Calculatrice")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; background: transparent; border: none;")
        layout.addWidget(title)
        
        # Écran
        self.calc_display = QLineEdit()
        self.calc_display.setReadOnly(True)
        self.calc_display.setAlignment(Qt.AlignRight)
        self.calc_display.setText("0")
        self.calc_display.setMinimumHeight(80)
        self.calc_display.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 32px;
                font-weight: bold;
                color: #333;
            }
        """)
        layout.addWidget(self.calc_display)
        
        # Boutons
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('÷', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('×', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('C', 3, 0), ('0', 3, 1), ('=', 3, 2), ('+', 3, 3),
        ]
        
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(80, 70)  # Boutons plus grands
            btn.setCursor(Qt.PointingHandCursor)
            
            if text in ['=', 'C']:
                color = '#667eea'
            elif text in ['+', '-', '×', '÷']:
                color = '#3498db'
            else:
                color = '#ecf0f1'
            
            text_color = 'white' if text in ['=', 'C', '+', '-', '×', '÷'] else '#333'
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {text_color};
                    border: none;
                    border-radius: 12px;
                    font-size: 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            
            btn.clicked.connect(lambda checked, t=text: self.calc_button_clicked(t))
            buttons_layout.addWidget(btn, row, col)
        
        layout.addLayout(buttons_layout)
        container.setLayout(layout)
        
        # Variables calculatrice
        self.calc_current = "0"
        self.calc_operator = None
        self.calc_operand = None
        
        return container
    
    def calc_button_clicked(self, text):
        """Gérer les clics sur la calculatrice"""
        if text == 'C':
            self.calc_current = "0"
            self.calc_operator = None
            self.calc_operand = None
        elif text in ['+', '-', '×', '÷']:
            if self.calc_operand is not None and self.calc_operator is not None:
                self.calculate()
            self.calc_operand = float(self.calc_current)
            self.calc_operator = text
            self.calc_current = "0"
        elif text == '=':
            self.calculate()
        else:
            if self.calc_current == "0":
                self.calc_current = text
            else:
                self.calc_current += text
        
        self.calc_display.setText(self.calc_current)
    
    def calculate(self):
        """Effectuer le calcul"""
        if self.calc_operator and self.calc_operand is not None:
            current_val = float(self.calc_current)
            try:
                if self.calc_operator == '+':
                    result = self.calc_operand + current_val
                elif self.calc_operator == '-':
                    result = self.calc_operand - current_val
                elif self.calc_operator == '×':
                    result = self.calc_operand * current_val
                elif self.calc_operator == '÷':
                    result = self.calc_operand / current_val if current_val != 0 else 0
                
                self.calc_current = str(result)
            except Exception:
                self.calc_current = "Error"
                
            self.calc_operator = None
            self.calc_operand = None
    
    def create_stats_widget(self):
        """Créer le widget de statistiques"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("📈 Statistiques du Jour")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; background: transparent; border: none;")
        layout.addWidget(title)
        
        # Placeholder stats
        stats = [
            ("💰 Ventes", "...", "#2ecc71"),
            ("🛒 Transactions", "...", "#3498db"),
        ]
        
        for label, value, color in stats:
            stat_widget = self.create_stat_item(label, value, color)
            layout.addWidget(stat_widget)
        
        layout.addStretch()
        container.setLayout(layout)
        
        return container
    
    def create_stat_item(self, label, value, color):
        """Créer un élément de statistique"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border-left: 4px solid {color};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: #333; font-size: 14px; background: transparent; border: none;")
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(value_widget)
        
        widget.setLayout(layout)
        return widget
