# -*- coding: utf-8 -*-
"""
Interface de gestion des produits
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QMenu, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from modules.products.product_manager import product_manager
from core.logger import logger

class ProductFormDialog(QDialog):
    """Dialogue d'ajout/modification de produit"""
    
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Nouveau Produit" if not product else "Modifier Produit")
        self.setMinimumWidth(500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Onglets pour organiser les informations
        tabs = QTabWidget()
        
        # Onglet Général
        general_tab = QWidget()
        form_layout = QFormLayout()
        
        self.barcode_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.name_ar_edit = QLineEdit()
        self.category_combo = QComboBox() # TODO: Charger les catégories
        self.description_edit = QLineEdit()
        
        form_layout.addRow("Code-barres:", self.barcode_edit)
        form_layout.addRow("Nom *:", self.name_edit)
        form_layout.addRow("Nom (Arabe):", self.name_ar_edit)
        form_layout.addRow("Description:", self.description_edit)
        # form_layout.addRow("Catégorie:", self.category_combo)
        
        general_tab.setLayout(form_layout)
        tabs.addTab(general_tab, "Général")
        
        # Onglet Prix & Stock
        price_tab = QWidget()
        price_layout = QFormLayout()
        
        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0, 1000000)
        self.purchase_price_spin.setSuffix(" DA")
        
        self.selling_price_spin = QDoubleSpinBox()
        self.selling_price_spin.setRange(0, 1000000)
        self.selling_price_spin.setSuffix(" DA")
        
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 100000)
        
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setRange(0, 1000)
        self.min_stock_spin.setValue(10)
        
        self.expiry_date_edit = QDateEdit()
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        self.enable_expiry = QCheckBox("Date d'expiration ?")
        self.enable_expiry.toggled.connect(self.expiry_date_edit.setEnabled)
        self.expiry_date_edit.setEnabled(False)
        
        price_layout.addRow("Prix d'achat:", self.purchase_price_spin)
        price_layout.addRow("Prix de vente *:", self.selling_price_spin)
        price_layout.addRow("Stock initial:", self.stock_spin)
        price_layout.addRow("Alert Stock Min:", self.min_stock_spin)
        price_layout.addRow(self.enable_expiry, self.expiry_date_edit)
        
        price_tab.setLayout(price_layout)
        tabs.addTab(price_tab, "Prix & Stock")
        
        layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Remplir si modification
        if self.product:
            self.barcode_edit.setText(self.product.get('barcode', ''))
            self.name_edit.setText(self.product.get('name', ''))
            self.name_ar_edit.setText(self.product.get('name_ar', ''))
            self.description_edit.setText(self.product.get('description', ''))
            self.purchase_price_spin.setValue(self.product.get('purchase_price', 0))
            self.selling_price_spin.setValue(self.product.get('selling_price', 0))
            self.stock_spin.setValue(self.product.get('stock_quantity', 0))
            self.min_stock_spin.setValue(self.product.get('min_stock_level', 10))
            
            if self.product.get('expiry_date'):
                self.enable_expiry.setChecked(True)
                self.expiry_date_edit.setDate(QDate.fromString(self.product['expiry_date'], "yyyy-MM-dd"))
                
    def save(self):
        if not self.name_edit.text() or self.selling_price_spin.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le nom et le prix de vente sont obligatoires.")
            return

        data = {
            'barcode': self.barcode_edit.text(),
            'name': self.name_edit.text(),
            'name_ar': self.name_ar_edit.text(),
            'description': self.description_edit.text(),
            'purchase_price': self.purchase_price_spin.value(),
            'selling_price': self.selling_price_spin.value(),
            'stock_quantity': self.stock_spin.value(),
            'min_stock_level': self.min_stock_spin.value(),
            'expiry_date': self.expiry_date_edit.date().toString("yyyy-MM-dd") if self.enable_expiry.isChecked() else None
        }
        
        if self.product:
            success, msg = product_manager.update_product(self.product['id'], **data)
        else:
            success, msg, pid = product_manager.create_product(**data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class ProductsPage(QWidget):
    """Page de gestion des produits"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_products()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher (Nom, Code-barres)...")
        self.search_input.textChanged.connect(self.load_products)
        toolbar.addWidget(self.search_input)
        
        # Filtres
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous les produits", "Stock faible", "En promotion", "Expire bientôt"])
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        toolbar.addWidget(self.filter_combo)
        
        # Bouton Nouveau
        new_btn = QPushButton("➕ Nouveau Produit")
        new_btn.setStyleSheet("background-color: #3498db; color: white;")
        new_btn.clicked.connect(self.open_new_product_dialog)
        toolbar.addWidget(new_btn)
        
        layout.addLayout(toolbar)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Prix Vente", "Stock", "Expiration", "Promotion", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Fixed
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_products(self):
        search = self.search_input.text()
        filter_mode = self.filter_combo.currentText()
        
        products = []
        if filter_mode == "Stock faible":
            products = product_manager.get_low_stock_products()
        elif filter_mode == "En promotion":
            products = product_manager.get_promoted_products()
        elif filter_mode == "Expire bientôt":
            products = product_manager.get_expiring_products()
        else:
            products = product_manager.search_products(search) if search else product_manager.get_all_products(limit=100)
            
        self.table.setRowCount(0)
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Stock alert color
            bg_color = None
            if p['stock_quantity'] <= p['min_stock_level']:
                bg_color = QColor("#ffebee") # Rouge clair
            
            # Items
            items = [
                p.get('barcode', ''),
                p['name'],
                f"{p['selling_price']} DA",
                str(p['stock_quantity']),
                p.get('expiry_date', '-'),
                f"{p.get('discount_percentage', 0)}%" if p.get('is_on_promotion') else "-"
            ]
            
            for i, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                if bg_color:
                    item.setBackground(bg_color)
                self.table.setItem(row, i, item)
                
            # Boutons Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, x=p: self.open_edit_dialog(x))
            
            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=p['id']: self.delete_product(x))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 6, action_widget)
            
    def open_new_product_dialog(self):
        dialog = ProductFormDialog(parent=self)
        if dialog.exec_():
            self.load_products()
            
    def open_edit_dialog(self, product):
        dialog = ProductFormDialog(product, parent=self)
        if dialog.exec_():
            self.load_products()
            
    def delete_product(self, product_id):
        confirm = QMessageBox.question(self, "Confirmer", "Supprimer ce produit ?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            product_manager.delete_product(product_id)
            self.load_products()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Obtenir le produit sélectionné
        row = self.table.currentRow()
        if row < 0:
            return
            
        # TODO: ID is tricky to get from row if not stored. 
        # Better storing objects or ID in hidden column. 
        # For now, I rely on the search providing the same order but that's risky.
        # Let's fix this in load_products by storing ID in UserRole.
        pass # To be implemented if requested, simpler actions button covers it.

    def refresh(self):
        """Rafraîchir les données"""
        self.load_products()
