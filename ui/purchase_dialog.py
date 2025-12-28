# -*- coding: utf-8 -*-
"""
Dialogue pour ajouter un achat chez un fournisseur
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, 
                             QPushButton, QDoubleSpinBox, QLineEdit, QMessageBox)
from core.i18n import i18n_manager
from PyQt5.QtCore import Qt

class PurchaseDialog(QDialog):
    """Dialogue d'ajout d'achat fournisseur"""
    def __init__(self, supplier, supplier_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.supplier_manager = supplier_manager
        self.auth_manager = auth_manager
        _ = i18n_manager.get
        self.setWindowTitle(_("purchase_dialog_title").format(supplier['company_name']))
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        
        info = QLabel(_("label_supplier_info").format(self.supplier['company_name']))
        info.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        layout.addWidget(info)
        
        form = QFormLayout()
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(1000)
        self.amount_spin.setDecimals(2)
        
        self.debt_spin = QDoubleSpinBox()
        self.debt_spin.setRange(0, 999999999)
        self.debt_spin.setSuffix(" DA")
        self.debt_spin.setValue(0)
        self.debt_spin.setDecimals(2)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText(_("placeholder_purchase_note"))
        
        form.addRow(_("label_purchase_amount"), self.amount_spin)
        form.addRow(_("label_debt_to_add"), self.debt_spin)
        form.addRow(_("label_payment_note"), self.notes_edit)
        
        layout.addLayout(form)
        
        # Info
        info_label = QLabel(_("info_purchase_msg"))
        info_label.setStyleSheet("color: gray; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Boutons
        btn_layout = QVBoxLayout()
        save_btn = QPushButton(_("btn_save_purchase"))
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton(_("btn_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def save(self):
        amount = self.amount_spin.value()
        debt = self.debt_spin.value()
        
        debt = self.debt_spin.value()
        _ = i18n_manager.get
        
        if amount <= 0:
            QMessageBox.warning(self, _("title_error"), _("msg_amount_warning"))
            return
            
        user = self.auth_manager.get_current_user()
        user_id = user['id'] if user else 1
        
        # Ajouter l'achat (met à jour total_purchases et total_debt)
        success, msg = self.supplier_manager.add_purchase(
            self.supplier['id'], 
            amount, 
            debt,
            user_id, 
            self.notes_edit.text()
        )
        
        if success:
            QMessageBox.information(self, _("title_success"), msg)
            self.accept()
        else:
            QMessageBox.critical(self, _("title_error"), msg)
