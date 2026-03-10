# -*- coding: utf-8 -*-
"""
Interface de gestion des fournisseurs
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from modules.suppliers.supplier_manager import supplier_manager
from core.auth import auth_manager
from core.logger import logger
from ui.purchase_dialog import PurchaseDialog
from core.i18n import i18n_manager
from core.data_signals import data_signals

class SupplierFormDialog(QDialog):
    """Dialogue d'ajout/modification de fournisseur"""
    
    def __init__(self, supplier=None, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        _ = i18n_manager.get
        self.setWindowTitle(_("supplier_dialog_new") if not supplier else _("supplier_dialog_edit"))
        self.setMinimumWidth(420)
        self.setMinimumHeight(300)
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        
        from ui._styles import DIALOG_STYLE, GREEN_BTN, SECONDARY_BTN
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self.company_name_edit = QLineEdit()
        self.contact_person_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.address_edit = QLineEdit()
        
        layout.addRow(_("label_company"), self.company_name_edit)
        layout.addRow(_("label_contact"), self.contact_person_edit)
        layout.addRow(_("label_phone"), self.phone_edit)
        layout.addRow(_("label_email"), self.email_edit)
        layout.addRow(_("label_address"), self.address_edit)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton(_("btn_save"))
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.setMinimumHeight(38)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(GREEN_BTN)
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton(_("btn_cancel"))
        cancel_btn.setMinimumHeight(38)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(SECONDARY_BTN)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
        
        if self.supplier:
            self.company_name_edit.setText(self.supplier.get('company_name', ''))
            self.contact_person_edit.setText(self.supplier.get('contact_person', ''))
            self.phone_edit.setText(self.supplier.get('phone', ''))
            self.email_edit.setText(self.supplier.get('email', ''))
            self.address_edit.setText(self.supplier.get('address', ''))
            
    def save(self):
        _ = i18n_manager.get
        if not self.company_name_edit.text():
            QMessageBox.warning(self, _("title_error"), _("msg_company_required"))
            return
            
        data = {
            'company_name': self.company_name_edit.text(),
            'contact_person': self.contact_person_edit.text(),
            'phone': self.phone_edit.text(),
            'email': self.email_edit.text(),
            'address': self.address_edit.text()
        }
        
        if self.supplier:
            success, msg = supplier_manager.update_supplier(self.supplier['id'], **data)
        else:
            success, msg, _ = supplier_manager.create_supplier(**data)
            
        if success:
            self.accept()
        else:
            _ = i18n_manager.get
            QMessageBox.critical(self, _("title_error"), msg)

class DebtPaymentDialog(QDialog):
    """Dialogue de paiement de dette fournisseur"""
    def __init__(self, supplier, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        # Conversion sûre en float
        try:
            self.supplier['total_debt'] = float(self.supplier.get('total_debt', 0))
        except (ValueError, TypeError):
             self.supplier['total_debt'] = 0.0

        _ = i18n_manager.get
        self.setWindowTitle(_("debt_dialog_title").format(supplier['company_name']))
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        
        from ui._styles import DIALOG_STYLE, GREEN_BTN
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        info = QLabel(_("label_current_debt").format(f"{self.supplier['total_debt']:g}"))
        info.setStyleSheet("font-size: 15px; font-weight: bold; color: #ef4444;")
        layout.addWidget(info)
        
        form = QFormLayout()
        form.setSpacing(10)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, self.supplier['total_debt'])
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(min(1000, self.supplier['total_debt']))
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText(_("placeholder_payment_note"))
        
        form.addRow(_("label_payment_amount"), self.amount_spin)
        form.addRow(_("label_payment_note"), self.notes_edit)
        layout.addLayout(form)
        
        btn = QPushButton(_("btn_validate_payment"))
        btn.setMinimumHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(GREEN_BTN)
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def save(self):
        amount = self.amount_spin.value()
        if amount <= 0:
            return
            
        user = auth_manager.get_current_user()
        user_id = user['id'] if user else 1
        
        success, msg = supplier_manager.pay_debt(
            self.supplier['id'], amount, user_id, self.notes_edit.text()
        )
        
        if success:
            _ = i18n_manager.get
            QMessageBox.information(self, _("title_success"), msg)
            self.accept()
        else:
            QMessageBox.critical(self, _("title_error"), msg)

class SuppliersPage(QWidget):
    """Page de gestion des fournisseurs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_suppliers()
        
        i18n_manager.language_changed.connect(self.update_ui_text)
        data_signals.suppliers_changed.connect(self.load_suppliers)
        self.update_ui_text()
        
    def init_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        from ui._styles import (header_style, HEADER_TITLE_STYLE, HEADER_SUBTITLE_STYLE,
                                TABLE_STYLE, SEARCH_INPUT_STYLE, COMBO_STYLE, AMBER_BTN,
                                action_btn_style)
        
        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet(header_style("#f59e0b", "#d97706"))
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        self.header = QLabel(_("suppliers_title"))
        self.header.setStyleSheet(HEADER_TITLE_STYLE)
        title_layout.addWidget(self.header)
        
        self.subtitle = QLabel(_("suppliers_subtitle"))
        self.subtitle.setStyleSheet(HEADER_SUBTITLE_STYLE)
        title_layout.addWidget(self.subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Toolbar - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_supplier"))
        self.search_input.setMinimumHeight(44)
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.textChanged.connect(self.load_suppliers)
        toolbar.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(44)
        self.filter_combo.setMinimumWidth(170)
        self.filter_combo.addItems([_("filter_all_suppliers"), _("filter_debt_suppliers")])
        self.filter_combo.setStyleSheet(COMBO_STYLE)
        self.filter_combo.currentIndexChanged.connect(self.load_suppliers)
        toolbar.addWidget(self.filter_combo)
        
        self.new_btn = QPushButton(_("btn_new_supplier"))
        self.new_btn.setMinimumHeight(44)
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.setStyleSheet(AMBER_BTN)
        self.new_btn.clicked.connect(self.open_new_dialog)
        toolbar.addWidget(self.new_btn)
        
        layout.addLayout(toolbar)
        
        # Table - Style amélioré
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(_("table_headers_suppliers"))
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_suppliers(self):
        _ = i18n_manager.get
        search = self.search_input.text()
        filter_idx = self.filter_combo.currentIndex()
        
        if filter_idx == 1: # Debt
            suppliers = supplier_manager.get_suppliers_with_debt()
        else:
            suppliers = supplier_manager.search_suppliers(search) if search else supplier_manager.get_all_suppliers()
            
        self.table.setRowCount(0)
        for s in suppliers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(s['code']))
            self.table.setItem(row, 1, QTableWidgetItem(s['company_name']))
            self.table.setItem(row, 2, QTableWidgetItem(s.get('contact_person', '')))
            self.table.setItem(row, 3, QTableWidgetItem(s.get('phone', '')))
            
            # Total Achats
            try:
                total_purchases = float(s.get('total_purchases', 0))
            except (ValueError, TypeError):
                total_purchases = 0.0
                
            purchases_item = QTableWidgetItem(f"{total_purchases:g} DA")
            purchases_item.setForeground(QColor("#3498db"))
            self.table.setItem(row, 4, purchases_item)
            
            # Dettes
            try:
                total_debt = float(s.get('total_debt', 0))
            except (ValueError, TypeError):
                total_debt = 0.0
                
            debt_item = QTableWidgetItem(f"{total_debt:g} DA")
            if total_debt > 0:
                debt_item.setForeground(QColor("red"))
            self.table.setItem(row, 5, debt_item)
            
            # Actions
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip(_("btn_edit"))
            edit_btn.clicked.connect(lambda checked, x=s: self.open_edit_dialog(x))
            hbox.addWidget(edit_btn)
            
            # Bouton pour ajouter dette/achat
            add_purchase_btn = QPushButton("🛒")
            add_purchase_btn.setToolTip(_("btn_add_purchase"))
            add_purchase_btn.setStyleSheet("color: blue;")
            add_purchase_btn.clicked.connect(lambda checked, x=s: self.open_purchase_dialog(x))
            hbox.addWidget(add_purchase_btn)
            
            if total_debt > 0:
                pay_btn = QPushButton("💸")
                pay_btn.setToolTip(_("btn_pay_debt"))
                pay_btn.setStyleSheet("color: green;")
                pay_btn.clicked.connect(lambda checked, x=s: self.open_payment_dialog(x))
                hbox.addWidget(pay_btn)

            # Bouton Supprimer
            del_btn = QPushButton("🗑️")
            del_btn.setToolTip(_("btn_delete"))
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=s['id']: self.delete_supplier(x))
            hbox.addWidget(del_btn)
                
            self.table.setCellWidget(row, 6, widget)
            
    def open_new_dialog(self):
        if SupplierFormDialog(parent=self).exec_():
            self.load_suppliers()
            
    def open_edit_dialog(self, supplier):
        if SupplierFormDialog(supplier, parent=self).exec_():
            self.load_suppliers()
            
    def open_payment_dialog(self, supplier):
        if DebtPaymentDialog(supplier, parent=self).exec_():
            self.load_suppliers()

    def delete_supplier(self, supplier_id):
        """Supprimer un fournisseur"""
        _ = i18n_manager.get
        confirm = QMessageBox.question(self, _("confirm_delete_customer_title"), 
                                     _("msg_confirm_delete_supplier"), 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = supplier_manager.delete_supplier(supplier_id)
            if success:
                # QMessageBox.information(self, "Succès", "Fournisseur supprimé avec succès")
                self.load_suppliers()
            else:
                QMessageBox.warning(self, _("title_error"), msg)
    
    def open_purchase_dialog(self, supplier):
        """Ouvrir le dialogue d'ajout d'achat"""
        if PurchaseDialog(supplier, supplier_manager, auth_manager, parent=self).exec_():
            self.load_suppliers()

    def refresh(self):
        """Rafraîchir les données"""
        self.load_suppliers()
    
    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre/clair"""
        if is_dark:
            # Mode sombre
            table_style = """
                QTableWidget {
                    background-color: #34495e;
                    color: #ecf0f1;
                    gridline-color: #4a6785;
                    border: 1px solid #4a6785;
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #4a6785;
                }
                QTableWidget::item:selected {
                    background-color: #9b59b6;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #9b59b6;
                    color: white;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                }
            """
            input_style = """
                QLineEdit, QComboBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 2px solid #4a6785;
                    border-radius: 8px;
                    padding: 8px;
                }
                QLineEdit:focus, QComboBox:focus {
                    border-color: #9b59b6;
                }
            """
        else:
            # Mode clair
            table_style = """
                QTableWidget {
                    background-color: white;
                    color: #2c3e50;
                    gridline-color: #e0e0e0;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #e0e0e0;
                }
                QTableWidget::item:selected {
                    background-color: #9b59b6;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #9b59b6;
                    color: white;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                }
            """
            input_style = """
                QLineEdit, QComboBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                }
                QLineEdit:focus, QComboBox:focus {
                    border-color: #9b59b6;
                }
            """
        
        self.table.setStyleSheet(table_style)
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(input_style)

    def update_ui_text(self):
        """Mettre à jour les textes"""
        _ = i18n_manager.get
        is_rtl = i18n_manager.is_rtl()
        
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)
        
        self.header.setText(_("suppliers_title"))
        self.subtitle.setText(_("suppliers_subtitle"))
        self.search_input.setPlaceholderText(_("placeholder_search_supplier"))
        self.new_btn.setText(_("btn_new_supplier"))
        
        # Filters
        current_idx = self.filter_combo.currentIndex()
        self.filter_combo.setItemText(0, _("filter_all_suppliers"))
        self.filter_combo.setItemText(1, _("filter_debt_suppliers"))
        self.filter_combo.setCurrentIndex(current_idx)
        
        # Headers
        headers = _("table_headers_suppliers")
        self.table.setHorizontalHeaderLabels(headers)

