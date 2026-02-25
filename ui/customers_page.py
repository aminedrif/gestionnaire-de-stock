# -*- coding: utf-8 -*-
"""
Interface de gestion des clients
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from modules.customers.customer_manager import customer_manager
from core.auth import auth_manager
from core.logger import logger
from core.i18n import i18n_manager
from core.data_signals import data_signals

class CustomerFormDialog(QDialog):
    """Dialogue d'ajout/modification de client"""
    
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.customer = customer
        _ = i18n_manager.get
        self.setWindowTitle(_("customer_dialog_new") if not customer else _("customer_dialog_edit"))
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.credit_limit_spin = QDoubleSpinBox()
        self.credit_limit_spin.setRange(0, 1000000)
        self.credit_limit_spin.setValue(0)
        self.credit_limit_spin.setSuffix(" DA")
        
        layout.addRow(_("label_fullname"), self.name_edit)
        layout.addRow(_("label_phone"), self.phone_edit)
        layout.addRow(_("label_email"), self.email_edit)
        layout.addRow(_("label_address"), self.address_edit)
        layout.addRow(_("label_credit_limit"), self.credit_limit_spin)
        
        # Boutons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(_("btn_save"))
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton(_("btn_cancel"))
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
        _ = i18n_manager.get
        if not self.name_edit.text():
            QMessageBox.warning(self, _("title_error"), _("msg_name_required"))
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
            _ = i18n_manager.get
            QMessageBox.critical(self, _("title_error"), msg)

class PaymentDialog(QDialog):
    """Dialogue de paiement de crédit"""
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        # Conversion sûre en float
        try:
            self.customer['current_credit'] = float(self.customer.get('current_credit', 0))
        except (ValueError, TypeError):
             self.customer['current_credit'] = 0.0
             
        _ = i18n_manager.get
        self.setWindowTitle(_("payment_dialog_title").format(self.customer['full_name']))
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        
        info = QLabel(_("label_current_credit").format(self.customer['current_credit']))
        info.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(info)
        
        form = QFormLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, self.customer['current_credit'])
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(min(1000, self.customer['current_credit']))
        self.amount_spin.valueChanged.connect(self.update_remaining)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText(_("placeholder_note"))
        
        form.addRow(_("label_amount_pay"), self.amount_spin)
        form.addRow(_("label_note"), self.notes_edit)
        layout.addLayout(form)
        
        # Nouveau solde
        remaining = self.customer['current_credit'] - self.amount_spin.value()
        self.remaining_label = QLabel(_("label_new_balance").format(remaining))
        self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.remaining_label)
        
        # Checkbox imprimer reçu
        self.print_receipt_cb = QCheckBox(_("checkbox_print_payment"))
        self.print_receipt_cb.setChecked(True)
        self.print_receipt_cb.setStyleSheet("font-size: 13px; margin-top: 5px;")
        layout.addWidget(self.print_receipt_cb)
        
        btn = QPushButton(_("btn_validate_payment"))
        btn.clicked.connect(self.save)
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def update_remaining(self):
        """Mettre à jour le solde restant"""
        _ = i18n_manager.get
        remaining = self.customer['current_credit'] - self.amount_spin.value()
        self.remaining_label.setText(_("label_new_balance").format(remaining))
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
            # Print receipt if checkbox is checked
            if self.print_receipt_cb.isChecked():
                self.print_payment_receipt(amount)
            
            _ = i18n_manager.get
            QMessageBox.information(self, _("title_success"), msg)
            self.accept()
        else:
            _ = i18n_manager.get
            QMessageBox.critical(self, _("title_error"), msg)
    
    def print_payment_receipt(self, amount):
        """Generate and print a payment receipt"""
        from datetime import datetime
        from modules.sales.printer import printer_manager
        
        _ = i18n_manager.get
        receipt_data = {
            'sale_number': f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'sale_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'customer_name': self.customer['full_name'],
            'items': [{'product_name': _('receipt_item_payment'), 'quantity': 1, 'unit_price': amount, 'subtotal': amount}],
            'total_amount': amount,
            'payment_method': 'cash',
            'amount_paid': amount,
            'change_amount': 0,
            'notes': self.notes_edit.text() or _('default_payment_note')
        }
        
        try:
            printer_manager.print_receipt(receipt_data, "standard")
        except Exception as e:
            logger.warning(f"Erreur impression reçu paiement: {e}")

class CustomerHistoryDialog(QDialog):
    """Dialogue d'historique client (Crédits & Achats)"""
    
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        _ = i18n_manager.get
        self.setWindowTitle(_("history_title_customer").format(self.customer['full_name']))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        
        # Info Client Header
        header = QFrame()
        header.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; padding: 10px;")
        h_layout = QHBoxLayout(header)
        
        info_l = QLabel(f"<b>{self.customer['full_name']}</b><br>Code: {self.customer['code']}")
        info_l.setStyleSheet("font-size: 16px; color: #2c3e50;")
        
        credit_l = QLabel(f"{_('label_current_debt')}: <b>{self.customer.get('current_credit', 0)} DA</b>")
        credit_l.setStyleSheet("font-size: 16px; color: #e74c3c;")
        
        h_layout.addWidget(info_l)
        h_layout.addStretch()
        h_layout.addWidget(credit_l)
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_financial_tab(), "💰 " + _("tab_financial_history"))
        self.tabs.addTab(self.create_purchase_tab(), "🛒 " + _("tab_purchase_history"))
        layout.addWidget(self.tabs)
        
        # Close Button
        close_btn = QPushButton(_("btn_close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("min-width: 100px; padding: 8px;")
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def create_financial_tab(self):
        """Create tab for credit/payment history"""
        _ = i18n_manager.get
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            _("col_date"), _("col_type"), _("col_amount"), _("col_notes"), _("col_user")
        ])
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        # Load Data
        transactions = customer_manager.get_credit_history(self.customer['id'])
        table.setRowCount(len(transactions))
        
        for i, t in enumerate(transactions):
            table.setItem(i, 0, QTableWidgetItem(t['transaction_date']))
            
            # Type & Color
            t_type = t['transaction_type']
            type_str = _("type_payment") if t_type == 'payment' else _("type_credit")
            type_item = QTableWidgetItem(type_str)
            if t_type == 'payment':
                type_item.setForeground(QColor("green"))
            else:
                type_item.setForeground(QColor("red"))
            table.setItem(i, 1, type_item)
            
            table.setItem(i, 2, QTableWidgetItem(f"{t['amount']} DA"))
            table.setItem(i, 3, QTableWidgetItem(str(t.get('notes') or '')))
            table.setItem(i, 4, QTableWidgetItem(str(t.get('processed_by_name') or '')))
            
        layout.addWidget(table)
        return widget

    def create_purchase_tab(self):
        """Create tab for sales history"""
        _ = i18n_manager.get
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            _("col_date"), _("col_sale_no"), _("col_total"), _("col_payment_method"), _("col_cashier")
        ])
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        # Load Data
        sales = customer_manager.get_purchase_history(self.customer['id'], limit=100)
        table.setRowCount(len(sales))
        
        for i, s in enumerate(sales):
            table.setItem(i, 0, QTableWidgetItem(s['sale_date']))
            table.setItem(i, 1, QTableWidgetItem(s['sale_number']))
            table.setItem(i, 2, QTableWidgetItem(f"{s['total_amount']} DA"))
            table.setItem(i, 3, QTableWidgetItem(s['payment_method']))
            table.setItem(i, 4, QTableWidgetItem(str(s.get('cashier_name') or '')))
            
        layout.addWidget(table)
        return widget

class CustomersPage(QWidget):
    """Page de gestion des clients"""
    navigate_to = pyqtSignal(str, dict) # Pour naviguer vers l'historique avec un filtre
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_customers()
        
        i18n_manager.language_changed.connect(self.update_ui_text)
        data_signals.customers_changed.connect(self.load_customers)
        self.update_ui_text()
        
    def init_ui(self):
        # Create a main layout if it doesn't exist
        if not self.layout():
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)
        
        # Create fresh container
        self.container = QWidget()
        self.layout().addWidget(self.container)
        
        # Build UI inside container
        self.build_ui_content(self.container)

    def update_ui_text(self):
        """Mettre à jour les textes de l'interface"""
        # Remove old container
        if hasattr(self, 'container'):
            if self.layout():
                self.layout().removeWidget(self.container)
            self.container.deleteLater()
        
        # Create new container
        self.container = QWidget()
        self.layout().addWidget(self.container)
        
        # Update layout direction
        if i18n_manager.is_rtl():
             self.setLayoutDirection(Qt.RightToLeft)
        else:
             self.setLayoutDirection(Qt.LeftToRight)
        
        # Rebuild UI
        self.build_ui_content(self.container)
        
        # Reload Data
        self.load_customers()

    def build_ui_content(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        layout.setSpacing(15)
        
        _ = i18n_manager.get
        
        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        header_lbl = QLabel(_("customers_title"))
        header_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        title_layout.addWidget(header_lbl)
        
        subtitle_lbl = QLabel(_("customers_subtitle"))
        subtitle_lbl.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        title_layout.addWidget(subtitle_lbl)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Toolbar - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_customer"))
        self.search_input.setMinimumHeight(50)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 15px;
                background-color: white;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #10b981;
                background-color: #ecfdf5;
            }
        """)
        self.search_input.textChanged.connect(self.load_customers)
        toolbar.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(50)
        self.filter_combo.setMinimumWidth(200)
        self.filter_combo.addItems([
            _("filter_all_customers"), 
            _("filter_with_debt"), 
            _("filter_best_customers")
        ])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 14px;
                background-color: white;
                color: #374151;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self.load_customers)
        toolbar.addWidget(self.filter_combo)
        
        self.new_btn = QPushButton(_("btn_new_customer"))
        self.new_btn.setMinimumHeight(50)
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        self.new_btn.clicked.connect(self.open_new_dialog)
        toolbar.addWidget(self.new_btn)
        
        layout.addLayout(toolbar)
        
        # Table - Style amélioré
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(_("table_headers_customers"))
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: transparent;
                background-color: white;
                selection-background-color: #ecfdf5;
                selection-color: #064e3b;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f0fdf4;
                padding: 10px 15px;
                border: none;
                border-bottom: 2px solid #bbf7d0;
                font-weight: bold;
                color: #166534;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px 10px;
                border-bottom: 1px solid #f0fdf4;
            }
            QTableWidget::item:selected {
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f0fdf4;
            }
        """)

        layout.addWidget(self.table)

        
    def load_customers(self):
        _ = i18n_manager.get
        search = self.search_input.text()
        # Use index instead of text for filter logic to be language independent
        filter_idx = self.filter_combo.currentIndex()
        
        if filter_idx == 1: # With debt
            customers = customer_manager.get_customers_with_credit()
        else:
            customers = customer_manager.search_customers(search) if search else customer_manager.get_all_customers()
            
        # Tri pour "Meilleurs clients" (Index 2)
        if filter_idx == 2:
            customers.sort(key=lambda x: x['total_purchases'], reverse=True)
            
        self.table.setRowCount(0)
        for c in customers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(c['code']))
            self.table.setItem(row, 1, QTableWidgetItem(c['full_name']))
            self.table.setItem(row, 2, QTableWidgetItem(c.get('phone', '')))
            
            try:
                current_credit = float(c.get('current_credit', 0))
            except (ValueError, TypeError):
                current_credit = 0.0
                
            try:
                total_purchases = float(c.get('total_purchases', 0))
            except (ValueError, TypeError):
                total_purchases = 0.0

            credit_item = QTableWidgetItem(f"{current_credit:g} DA")
            if current_credit > 0:
                credit_item.setForeground(QColor("red"))
            self.table.setItem(row, 3, credit_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(f"{total_purchases:g} DA"))
            
            # Actions
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(5, 0, 5, 0)
            hbox.setSpacing(5)
            
            # Helper for styled buttons
            def make_btn(text, tooltip, color, hover_bg):
                btn = QPushButton(text)
                btn.setToolTip(tooltip)
                btn.setFixedSize(35, 35)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid #e5e7eb;
                        border-radius: 6px;
                        color: {color};
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_bg};
                        border-color: {color};
                    }}
                """)
                return btn

            edit_btn = make_btn("✏️", _("tooltip_edit"), "#3b82f6", "#eff6ff")
            edit_btn.clicked.connect(lambda checked, x=c: self.open_edit_dialog(x))
            hbox.addWidget(edit_btn)
            
            pay_btn = make_btn("💰", _("tooltip_pay_debt"), "#10b981", "#ecfdf5")
            pay_btn.clicked.connect(lambda checked, x=c: self.open_payment_dialog(x))
            hbox.addWidget(pay_btn)
            
            hist_btn = make_btn("📜", _("tooltip_history"), "#6b7280", "#f3f4f6")
            hist_btn.clicked.connect(lambda checked, x=c: self.open_history_dialog(x))
            hbox.addWidget(hist_btn)
            
            del_btn = make_btn("🗑️", _("tooltip_delete"), "#ef4444", "#fef2f2")
            del_btn.clicked.connect(lambda checked, x=c['id']: self.delete_customer(x))
            hbox.addWidget(del_btn)
            
            self.table.setCellWidget(row, 5, widget)
            
        # Adjust column width for actions
        self.table.setColumnWidth(5, 180)
            
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
        _ = i18n_manager.get
        confirm = QMessageBox.question(self, _("confirm_delete_customer_title"), 
                                     _("confirm_delete_customer_msg"), 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = customer_manager.delete_customer(customer_id)
            if success:
                self.load_customers()
            else:
                QMessageBox.warning(self, _("msg_delete_error"), msg)

    def open_history(self, customer_name):
        """Ouvrir le dialogue d'historique pour ce client"""
        # Find customer object first (since we only got name passed in lambda)
        # Ideally we should pass the whole object, let's fix the lambda in load_customers
        pass 
        
    def open_history_dialog(self, customer):
        """Nouvelle méthode pour ouvrir le dialogue dédié"""
        dialog = CustomerHistoryDialog(customer, parent=self)
        dialog.exec_()

    def refresh(self):
        """Rafraîchir les données"""
        self.load_customers()
    
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
                    background-color: #27ae60;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #27ae60;
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
                    border-color: #27ae60;
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
                    background-color: #27ae60;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #27ae60;
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
                    border-color: #27ae60;
                }
            """
        
        self.table.setStyleSheet(table_style)
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(input_style)

