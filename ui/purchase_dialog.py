# -*- coding: utf-8 -*-
"""
Dialogue pour ajouter un achat chez un fournisseur (avec gestion stocks & finance)
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                             QPushButton, QDoubleSpinBox, QSpinBox, QLineEdit, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, 
                             QGroupBox, QWidget, QAbstractItemView, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

from core.i18n import i18n_manager
from core.logger import logger
from modules.products.product_manager import product_manager


class PurchaseDialog(QDialog):
    """Dialogue d'achat fournisseur complet"""
    
    def __init__(self, supplier, supplier_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.supplier_manager = supplier_manager
        self.auth_manager = auth_manager
        
        self.cart_items = []  # List of objects/dicts
        
        _ = i18n_manager.get
        self.setWindowTitle(_("purchase_dialog_title").format(supplier['company_name']))
        self.resize(1100, 700)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        
        # === LEFT PANEL: SEARCH ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search Bar
        _ = i18n_manager.get
        search_group = QGroupBox(_("purchase_search_group"))
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_scan"))
        self.search_input.setMinimumHeight(45)
        self.search_input.setStyleSheet("font-size: 14px; padding: 5px;")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            _("table_header_product"), _("table_header_stock"), 
            _("table_header_purchase_price"), _("table_header_action")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.cellDoubleClicked.connect(self.on_result_double_click)
        search_layout.addWidget(self.results_table)
        
        search_group.setLayout(search_layout)
        left_layout.addWidget(search_group)
        
        layout.addWidget(left_panel, 4) # 40% width
        
        # === RIGHT PANEL: CART & PAYMENT ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Cart Group
        _ = i18n_manager.get
        cart_group = QGroupBox(_("group_cart").format(self.supplier['company_name']))
        cart_layout = QVBoxLayout()
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            _("table_header_product"), _("table_header_qty"), 
            _("table_header_unit_price"), _("table_header_total"), ""
        ])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        cart_layout.addWidget(self.cart_table)
        
        cart_group.setLayout(cart_layout)
        right_layout.addWidget(cart_group, 2)
        
        # Payment Group
        _ = i18n_manager.get
        pay_group = QGroupBox(_("group_payment"))
        pay_layout = QFormLayout()
        
        # Total Label
        self.lbl_total = QLabel("0.00 DA")
        self.lbl_total.setFont(QFont("Arial", 18, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #e74c3c;")
        pay_layout.addRow(_("label_total_to_pay"), self.lbl_total)
        
        # Payment Source
        self.combo_source = QComboBox()
        self.combo_source.addItems([
            _("payment_cash"), _("payment_credit")
        ])
        self.combo_source.currentIndexChanged.connect(self.update_payment_ui)
        pay_layout.addRow(_("label_payment_source"), self.combo_source)
        
        # Amount Paid
        self.spin_paid = QDoubleSpinBox()
        self.spin_paid.setRange(0, 99999999)
        self.spin_paid.setSuffix(" DA")
        self.spin_paid.setDecimals(2)
        self.spin_paid.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.spin_paid.valueChanged.connect(self.update_debt_label)
        pay_layout.addRow(_("label_amount_paid"), self.spin_paid)
        
        # Remaining Debt
        self.lbl_debt = QLabel("0.00 DA")
        self.lbl_debt.setStyleSheet("font-weight: bold; color: gray;")
        pay_layout.addRow(_("label_remaining_debt"), self.lbl_debt)
        
        self.txt_notes = QLineEdit()
        self.txt_notes.setPlaceholderText(_("label_notes"))
        pay_layout.addRow(_("label_notes"), self.txt_notes)
        
        pay_group.setLayout(pay_layout)
        right_layout.addWidget(pay_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton(_("btn_validate_purchase"))
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 16px;")
        self.btn_save.clicked.connect(self.validate_purchase)
        
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setMinimumHeight(50)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        right_layout.addLayout(btn_layout)
        
        layout.addWidget(right_panel, 6) # 60% width

        # Initialize
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.perform_search)
        
        self.search_input.setFocus()
        self.perform_search() # Load initial list (top 20)

    def on_search_changed(self):
        self.timer.start(300) # Debounce 300ms
        
    def perform_search(self):
        query = self.search_input.text().strip()
        if query:
            products = product_manager.search_products(query)
        else:
            products = product_manager.get_all_products(limit=30)

        self.results_table.setRowCount(0)
        for p in products:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(f"{p['name']}\n{p.get('barcode','')}")
            name_item.setData(Qt.UserRole, p)
            self.results_table.setItem(row, 0, name_item)
            
            # Stock
            self.results_table.setItem(row, 1, QTableWidgetItem(str(p['stock_quantity'])))
            
            # Price
            self.results_table.setItem(row, 2, QTableWidgetItem(f"{p['purchase_price']:.2f}"))
            
            # Add Button
            btn = QPushButton("➕")
            btn.setStyleSheet("color: green; font-weight: bold;")
            btn.clicked.connect(lambda ch, prod=p: self.add_to_cart(prod))
            self.results_table.setCellWidget(row, 3, btn)
            
        self.results_table.resizeRowsToContents()

    def on_result_double_click(self, row, col):
        item = self.results_table.item(row, 0)
        if item:
            product = item.data(Qt.UserRole)
            self.add_to_cart(product)

    def add_to_cart(self, product):
        # Check if already in cart
        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 0)
            if item and item.data(Qt.UserRole)['id'] == product['id']:
                # Already exists, maybe increment qty
                qty_spin = self.cart_table.cellWidget(row, 1)
                qty_spin.setValue(qty_spin.value() + 1)
                return

        # Add new row
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        
        # Name
        name_item = QTableWidgetItem(product['name'])
        name_item.setData(Qt.UserRole, product)
        self.cart_table.setItem(row, 0, name_item)
        
        # Qty Spin
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 9999)
        qty_spin.setValue(1)
        qty_spin.valueChanged.connect(self.update_totals)
        self.cart_table.setCellWidget(row, 1, qty_spin)
        
        # Price Spin (Editable Purchase Price)
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0, 99999999)
        price_spin.setDecimals(2)
        price_spin.setValue(float(product['purchase_price'] or 0))
        price_spin.valueChanged.connect(self.update_totals)
        self.cart_table.setCellWidget(row, 2, price_spin)
        
        # Total Item
        self.cart_table.setItem(row, 3, QTableWidgetItem("0.00"))
        
        # Remove Btn
        del_btn = QPushButton("❌")
        del_btn.setStyleSheet("color: red; border: none;")
        del_btn.clicked.connect(lambda: self.remove_cart_item(del_btn))
        self.cart_table.setCellWidget(row, 4, del_btn)
        
        self.update_totals()

    def remove_cart_item(self, btn):
        # Find row containing this button
        for row in range(self.cart_table.rowCount()):
            if self.cart_table.cellWidget(row, 4) == btn:
                self.cart_table.removeRow(row)
                self.update_totals()
                return

    def update_totals(self):
        total = 0.0
        for row in range(self.cart_table.rowCount()):
            qty = self.cart_table.cellWidget(row, 1).value()
            price = self.cart_table.cellWidget(row, 2).value()
            row_total = qty * price
            
            self.cart_table.item(row, 3).setText(f"{row_total:.2f}")
            total += row_total
            
        self.lbl_total.setText(f"{total:.2f} DA")
        self.lbl_total.setProperty("total_value", total)
        
        # Update paid spin default if it matches total previously (or strictly equal)
        # Actually logic: if "Paid" is meant to be full, keep it full?
        # User logic: usually pays full.
        # But if user manually set it, don't overwrite?
        # Simple logic: Update paid amount to match total IF payment source is NOT Credit
        if self.combo_source.currentIndex() != 1: # Not Credit
           self.spin_paid.setValue(total)
           
        self.update_debt_label()

    def update_payment_ui(self):
        source_idx = self.combo_source.currentIndex()
        total = self.lbl_total.property("total_value") or 0.0
        
        if source_idx == 1: # Credit
            self.spin_paid.setValue(0)
            self.spin_paid.setEnabled(True)
        else: # Coffre or Caisse
            self.spin_paid.setValue(total)
            self.spin_paid.setEnabled(True)
            
        self.update_debt_label()

    def update_debt_label(self):
        total = self.lbl_total.property("total_value") or 0.0
        paid = self.spin_paid.value()
        debt = total - paid
        
        if debt < 0:
             self.lbl_debt.setText("0.00 DA (Trop perçu ?)")
             self.lbl_debt.setStyleSheet("color: red; font-weight: bold;")
        else:
             self.lbl_debt.setText(f"{debt:.2f} DA")
             self.lbl_debt.setStyleSheet("color: gray; font-weight: bold;")

    def validate_purchase(self):
        row_count = self.cart_table.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "Erreur", "Le panier est vide")
            return
            
        total = self.lbl_total.property("total_value") or 0.0
        paid = self.spin_paid.value()
        
        # Adjust based on selection:
        # Index 0 = Cash -> Paid should be total? Or user enters it?
        # Index 1 = Credit -> Paid usually 0? Or partial?
        # User can edit spin_paid manually.
        # But if Credit is selected, maybe default to 0? Or user choice.
        # Logic relies on 'paid' amount regardless of source.
        
        debt = total - paid
        
        if paid > total:
            QMessageBox.warning(self, "Erreur", "Le montant payé ne peut pas dépasser le total")
            return

        # Safe balance check removed - finance system disabled

        # Double check with user
        reply = QMessageBox.question(self, "Confirmer Achat", 
                                     f"Valider l'achat de {row_count} articles pour {total:.2f} DA ?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return

        # DO IT
        try:
            user_id = self.auth_manager.current_user['id']
            notes = self.txt_notes.text()
            
            # 1. Update Products Stock & Cost
            items_details = []
            for row in range(row_count):
                product = self.cart_table.item(row, 0).data(Qt.UserRole)
                qty = self.cart_table.cellWidget(row, 1).value()
                price = self.cart_table.cellWidget(row, 2).value()
                
                # Update Stock
                product_manager.update_stock(product['id'], qty, "Achat Fournisseur")
                
                # Update Cost Price (Optional: Weighted Average? Or Last Price?)
                # Usually Last Price is preferred for simple POS.
                if price > 0 and price != product['purchase_price']:
                    product_manager.update_product(product['id'], purchase_price=price)
                
                items_details.append(f"{product['name']} x{qty}")

            # 2. Add Purchase to Supplier Manager
            # This updates supplier stats (Total purchases, Total Debt)
            # add_purchase(supplier_id, purchase_amount, debt_amount, ...)
            desc = f"Achat {len(items_details)} produits. " + notes
            self.supplier_manager.add_purchase(self.supplier['id'], total, debt, user_id, desc)
            
            # 3. Handle Payment - Finance system removed
            # Payment tracking now simplified - only updates supplier records
            # if source_idx == 0 and paid > 0: # Coffre
            #      finance_manager.withdraw_from_safe(paid, f"Paiement Fournisseur {self.supplier['company_name']}", 
            #                                         user_id, supplier_id=self.supplier['id'])
            # elif source_idx == 2 and paid > 0: # Caisse
            #      pass
            
            # 4. If Debt > 0, it's already handled by add_purchase (increments total_debt)
            
            QMessageBox.information(self, "Succès", "Achat enregistré avec succès")
            self.accept()
            
        except Exception as e:
            logger.error(f"Erreur validation achat: {e}")
            QMessageBox.critical(self, "Erreur", str(e))
