# -*- coding: utf-8 -*-
"""
Interface de gestion des clients
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from modules.customers.customer_manager import customer_manager
from core.auth import auth_manager
from core.logger import logger

class CustomerFormDialog(QDialog):
    """Dialogue d'ajout/modification de client"""
    
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Nouveau Client" if not customer else "Modifier Client")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.credit_limit_spin = QDoubleSpinBox()
        self.credit_limit_spin.setRange(0, 1000000)
        self.credit_limit_spin.setValue(0)
        self.credit_limit_spin.setSuffix(" DA")
        
        layout.addRow("Nom Complet *:", self.name_edit)
        layout.addRow("Téléphone:", self.phone_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Adresse:", self.address_edit)
        layout.addRow("Limite de Crédit:", self.credit_limit_spin)
        
        # Boutons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
        
        if self.customer:
            self.name_edit.setText(self.customer.get('full_name', ''))
            self.phone_edit.setText(self.customer.get('phone', ''))
            self.email_edit.setText(self.customer.get('email', ''))
            self.address_edit.setText(self.customer.get('address', ''))
            self.credit_limit_spin.setValue(self.customer.get('credit_limit', 0))
            
    def save(self):
        if not self.name_edit.text():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return
            
        data = {
            'full_name': self.name_edit.text(),
            'phone': self.phone_edit.text(),
            'email': self.email_edit.text(),
            'address': self.address_edit.text(),
            'credit_limit': self.credit_limit_spin.value()
        }
        
        if self.customer:
            success, msg = customer_manager.update_customer(self.customer['id'], **data)
        else:
            success, msg, _ = customer_manager.create_customer(**data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class PaymentDialog(QDialog):
    """Dialogue de paiement de crédit"""
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle(f"Règlement Crédit: {self.customer['full_name']}")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        info = QLabel(f"Crédit actuel: {self.customer['current_credit']:.2f} DA")
        info.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(info)
        
        form = QFormLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, self.customer['current_credit'])
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(min(1000, self.customer['current_credit']))
        self.amount_spin.valueChanged.connect(self.update_remaining)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Note optionnelle...")
        
        form.addRow("Montant à régler:", self.amount_spin)
        form.addRow("Note:", self.notes_edit)
        layout.addLayout(form)
        
        # Nouveau solde
        self.remaining_label = QLabel(f"Nouveau solde: {(self.customer['current_credit'] - self.amount_spin.value()):.2f} DA")
        self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.remaining_label)
        
        btn = QPushButton("Valider Paiement")
        btn.clicked.connect(self.save)
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def update_remaining(self):
        """Mettre à jour le solde restant"""
        remaining = self.customer['current_credit'] - self.amount_spin.value()
        self.remaining_label.setText(f"Nouveau solde: {remaining:.2f} DA")
        if remaining < 0:
             self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
        else:
             self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
    def save(self):
        amount = self.amount_spin.value()
        if amount <= 0:
            return
            
        user = auth_manager.get_current_user()
        user_id = user['id'] if user else 1
        
        success, msg = customer_manager.pay_credit(
            self.customer['id'], amount, user_id, self.notes_edit.text()
        )
        
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class CustomersPage(QWidget):
    """Page de gestion des clients"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_customers()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher client...")
        self.search_input.textChanged.connect(self.load_customers)
        toolbar.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous les clients", "Avec dettes (Crédit > 0)", "Meilleurs clients"])
        self.filter_combo.currentIndexChanged.connect(self.load_customers)
        toolbar.addWidget(self.filter_combo)
        
        new_btn = QPushButton("➕ Nouveau Client")
        new_btn.setStyleSheet("background-color: #3498db; color: white;")
        new_btn.clicked.connect(self.open_new_dialog)
        toolbar.addWidget(new_btn)
        
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Téléphone", "Dette (Crédit)", "Total Achats", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_customers(self):
        search = self.search_input.text()
        filter_mode = self.filter_combo.currentText()
        
        if filter_mode == "Avec dettes (Crédit > 0)":
            customers = customer_manager.get_customers_with_credit()
        else:
            customers = customer_manager.search_customers(search) if search else customer_manager.get_all_customers()
            
        # Tri pour "Meilleurs clients"
        if filter_mode == "Meilleurs clients":
            customers.sort(key=lambda x: x['total_purchases'], reverse=True)
            
        self.table.setRowCount(0)
        for c in customers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(c['code']))
            self.table.setItem(row, 1, QTableWidgetItem(c['full_name']))
            self.table.setItem(row, 2, QTableWidgetItem(c.get('phone', '')))
            
            credit_item = QTableWidgetItem(f"{c['current_credit']:.2f} DA")
            if c['current_credit'] > 0:
                credit_item.setForeground(QColor("red"))
            self.table.setItem(row, 3, credit_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(f"{c['total_purchases']:.2f} DA"))
            
            # Actions
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, x=c: self.open_edit_dialog(x))
            hbox.addWidget(edit_btn)
            
            if c['current_credit'] > 0:
                pay_btn = QPushButton("💰")
                pay_btn.setToolTip("Régler Dette")
                pay_btn.setStyleSheet("color: green;")
                pay_btn.clicked.connect(lambda checked, x=c: self.open_payment_dialog(x))
                hbox.addWidget(pay_btn)
            
            # Delete button
            del_btn = QPushButton("🗑️")
            del_btn.setToolTip("Supprimer")
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=c['id']: self.delete_customer(x))
            hbox.addWidget(del_btn)
                
            self.table.setCellWidget(row, 5, widget)
            
    def open_new_dialog(self):
        if CustomerFormDialog(parent=self).exec_():
            self.load_customers()
            
    def open_edit_dialog(self, customer):
        if CustomerFormDialog(customer, parent=self).exec_():
            self.load_customers()
            
    def open_payment_dialog(self, customer):
        if PaymentDialog(customer, parent=self).exec_():
            self.load_customers()

    def delete_customer(self, customer_id):
        """Supprimer un client"""
        confirm = QMessageBox.question(self, "Confirmer", 
                                     "Voulez-vous vraiment supprimer ce client ?", 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = customer_manager.delete_customer(customer_id)
            if success:
                self.load_customers()
            else:
                QMessageBox.warning(self, "Impossible de supprimer", msg)

    def refresh(self):
        """Rafraîchir les données"""
        self.load_customers()
