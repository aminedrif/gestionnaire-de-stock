# -*- coding: utf-8 -*-
"""
Interface des paramètres
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QTabWidget,
                             QFormLayout, QGroupBox, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from core.auth import auth_manager
from core.logger import logger
from database.db_manager import db
import config
import openpyxl

class SettingsPage(QWidget):
    """Page de configuration"""
    
    # Signal pour changement de thème (si implémenté dynamiquement)
    theme_changed = pyqtSignal(bool) # True = Dark mode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_users()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        header = QLabel("⚙️ Paramètres")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Utilisateurs
        self.users_tab = self.create_users_tab()
        tabs.addTab(self.users_tab, "👥 Utilisateurs")
        self.appearance_tab = self.create_appearance_tab()
        tabs.addTab(self.appearance_tab, "🎨 Apparence")
        
        # Onglet Données (Export)
        self.data_tab = self.create_data_tab()
        tabs.addTab(self.data_tab, "💾 Données")

        # Onglet Magasin
        self.store_tab = self.create_store_tab()
        tabs.addTab(self.store_tab, "🏪 Magasin")
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_data_tab(self):
        """Onglet de gestion des données"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Exportation")
        form = QFormLayout()
        
        export_btn = QPushButton("📄 Exporter toutes les données (Excel)")
        export_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        export_btn.clicked.connect(self.export_data)
        
        info_lbl = QLabel("Exporte les Produits, Ventes, Clients et Paramètres dans un fichier Excel.")
        info_lbl.setStyleSheet("color: gray;")
        
        form.addRow(info_lbl)
        form.addRow(export_btn)
        group.setLayout(form)
        
        layout.addWidget(group)
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def export_data(self):
        """Exporter les données en Excel"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder les données", 
                                                    str(config.DATA_DIR / "backup.xlsx"), 
                                                    "Fichiers Excel (*.xlsx)")
            if not filename:
                return

            wb = openpyxl.Workbook()
            
            # 1. Produits
            ws_prod = wb.active
            ws_prod.title = "Produits"
            products = db.execute_query("SELECT barcode, name, purchase_price, selling_price, stock_quantity FROM products")
            ws_prod.append(["Code-barres", "Nom", "PA", "PV", "Stock"])
            for p in products:
                ws_prod.append([p['barcode'], p['name'], p['purchase_price'], p['selling_price'], p['stock_quantity']])
                
            # 2. Ventes
            ws_sales = wb.create_sheet("Ventes")
            sales = db.execute_query("SELECT sale_number, total_amount, payment_method, sale_date FROM sales")
            ws_sales.append(["N° Vente", "Montant Total", "Paiement", "Date"])
            for s in sales:
                ws_sales.append([s['sale_number'], s['total_amount'], s['payment_method'], s['sale_date']])

            # 3. Clients
            ws_cust = wb.create_sheet("Clients")
            customers = db.execute_query("SELECT full_name, phone, current_credit, total_purchases FROM customers")
            ws_cust.append(["Nom", "Téléphone", "Dette", "Total Achats"])
            for c in customers:
                ws_cust.append([c['full_name'], c['phone'], c['current_credit'], c['total_purchases']])
            
            wb.save(filename)
            QMessageBox.information(self, "Succès", f"Données exportées vers :\n{filename}")
            
        except Exception as e:
            logger.error(f"Erreur export excel: {e}")
            QMessageBox.critical(self, "Erreur", f"Échec de l'exportation: {e}")

    # ... (rest of methods)
        
    def create_users_tab(self):
        """Onglet de gestion des utilisateurs"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Liste des utilisateurs (Gauche)
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("<b>Liste des utilisateurs</b>"))
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["Utilisateur", "Nom", "Rôle"])
        self.users_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        list_layout.addWidget(self.users_table)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_users)
        list_layout.addWidget(refresh_btn)
        
        layout.addLayout(list_layout, 2)
        
        # Formulaire d'ajout (Droite)
        form_group = QGroupBox("Ajouter un utilisateur")
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.fullname_input = QLineEdit()
        self.role_input = QComboBox()
        self.role_input.addItem("Caissier", "cashier")
        self.role_input.addItem("Administrateur", "admin")
        
        form_layout.addRow("Nom d'utilisateur:", self.username_input)
        form_layout.addRow("Mot de passe:", self.password_input)
        form_layout.addRow("Nom complet:", self.fullname_input)
        form_layout.addRow("Rôle:", self.role_input)
        
        add_btn = QPushButton("➕ Créer l'utilisateur")
        add_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        add_btn.clicked.connect(self.add_user)
        form_layout.addRow(add_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group, 1)
        
        tab.setLayout(layout)
        return tab
        
    def create_appearance_tab(self):
        """Onglet apparence"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Thème")
        g_layout = QVBoxLayout()
        
        self.dark_mode_cb = QCheckBox("🌙 Activer le mode sombre")
        self.dark_mode_cb.clicked.connect(self.toggle_dark_mode)
        g_layout.addWidget(self.dark_mode_cb)
        
        group.setLayout(g_layout)
        layout.addWidget(group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_store_tab(self):
        """Onglet infos magasin"""
        tab = QWidget()
        layout = QFormLayout()
        
        self.store_name = QLineEdit("Mini-Market")
        self.store_phone = QLineEdit()
        self.store_address = QLineEdit()
        
        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "Info", "Paramètres sauvegardés (simulé)"))
        
        layout.addRow("Nom du magasin:", self.store_name)
        layout.addRow("Téléphone:", self.store_phone)
        layout.addRow("Adresse:", self.store_address)
        layout.addRow(save_btn)
        
        tab.setLayout(layout)
        return tab
        
    def load_users(self):
        """Charger la liste des utilisateurs"""
        try:
            query = "SELECT username, full_name, role FROM users"
            users = db.execute_query(query)
            
            self.users_table.setRowCount(0)
            for user in users:
                row = self.users_table.rowCount()
                self.users_table.insertRow(row)
                self.users_table.setItem(row, 0, QTableWidgetItem(user['username']))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['full_name']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['role']))
        except Exception as e:
            logger.error(f"Erreur chargement utilisateurs: {e}")
            
    def add_user(self):
        """Ajouter un utilisateur"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        fullname = self.fullname_input.text().strip()
        role = self.role_input.currentData()
        
        if not all([username, password, fullname]):
            QMessageBox.warning(self, "Erreur", "Tous les champs sont requis")
            return
            
        success, msg, _ = auth_manager.create_user(username, password, fullname, role)
        
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.username_input.clear()
            self.password_input.clear()
            self.fullname_input.clear()
            self.load_users()
        else:
            QMessageBox.critical(self, "Erreur", msg)
            
    def toggle_dark_mode(self):
        """Basculer le mode sombre"""
        is_dark = self.dark_mode_cb.isChecked()
        self.theme_changed.emit(is_dark) # Émettre le signal pour MainWindow
