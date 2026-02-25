# -*- coding: utf-8 -*-
"""
Interface Point de Vente (POS)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QSpinBox,
                             QDoubleSpinBox, QGroupBox, QGridLayout, QDialog,
                             QFormLayout, QInputDialog, QAbstractItemView, QShortcut, QTextBrowser,
                             QCheckBox, QCompleter, QScrollArea, QListView)
from PyQt5.QtCore import Qt, QTimer, QStringListModel, QSize, QEvent
from PyQt5.QtGui import QIcon, QPixmap
from pathlib import Path
# ... imports ...
from modules.sales.printer import printer_manager

from core.logger import logger
from core.i18n import i18n_manager
from core.data_signals import data_signals

class ReceiptPreviewDialog(QDialog):
    """Dialogue d'aperçu du ticket"""
    def __init__(self, sale_data, parent=None):
        super().__init__(parent)
        self.sale_data = sale_data
        _ = i18n_manager.get
        self.setWindowTitle(_("receipt_preview_title").format(sale_data['sale_number']))
        self.setMinimumSize(400, 600)
        # Apply RTL if needed
        self.setLayoutDirection(Qt.RightToLeft if i18n_manager.is_rtl() else Qt.LeftToRight)
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        
        # Aperçu HTML
        self.preview = QTextBrowser()
        html = printer_manager.preview_receipt(self.sale_data)
        self.preview.setHtml(html)
        layout.addWidget(self.preview)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton(_("btn_print"))
        print_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        print_btn.clicked.connect(self.print_ticket)
        
        close_btn = QPushButton(_("btn_close"))
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def print_ticket(self):
        _ = i18n_manager.get
        success, msg = printer_manager.print_receipt(self.sale_data)
        if success:
            QMessageBox.information(self, _("msg_success"), msg)
            self.accept()
        else:
            QMessageBox.warning(self, _("msg_error"), msg)


from PyQt5.QtGui import QFont, QColor, QKeySequence, QPixmap
from datetime import datetime
from modules.products.product_manager import product_manager
from modules.sales.cart import Cart
from modules.sales.pos import pos_manager
from modules.customers.customer_manager import customer_manager
from core.auth import auth_manager
from modules.sales.shortcuts_manager import shortcuts_manager
from ui.shortcut_config_dialog import ShortcutConfigDialog
from pathlib import Path

class ReturnDialog(QDialog):
    """Dialogue de gestion des retours"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sale_data = None
        self.setup_ui()
        self.update_ui_text()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Recherche Vente
        search_layout = QHBoxLayout()
        self.sale_id_input = QLineEdit()
        self.sale_id_input_btn = QPushButton()
        self.sale_id_input_btn.clicked.connect(self.search_sale)
        
        # Labels created here but text set in update_ui_text
        self.label_sale = QLabel()
        
        search_layout.addWidget(self.label_sale)
        search_layout.addWidget(self.sale_id_input)
        search_layout.addWidget(self.sale_id_input_btn)
        layout.addLayout(search_layout)
        
        # Info Vente
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-weight: bold; color: #34495e;")
        layout.addWidget(self.info_label)
        
        # Liste articles
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        # Headers set in update_ui_text
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.items_table)
        
        # Actions
        btn_layout = QHBoxLayout()
        self.cancel_sale_btn = QPushButton()
        self.cancel_sale_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        self.cancel_sale_btn.clicked.connect(self.cancel_entire_sale)
        
        self.process_return_btn = QPushButton()
        self.process_return_btn.setStyleSheet("background-color: #f39c12; color: white;")
        self.process_return_btn.clicked.connect(self.process_partial_return)
        
        btn_layout.addWidget(self.cancel_sale_btn)
        
        self.reprint_btn = QPushButton()
        self.reprint_btn.setStyleSheet("background-color: #3498db; color: white;")
        self.reprint_btn.clicked.connect(self.reprint_ticket)
        btn_layout.addWidget(self.reprint_btn)
        
        btn_layout.addWidget(self.process_return_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def update_ui_text(self):
        _ = i18n_manager.get
        self.setWindowTitle(_("return_dialog_title"))
        self.setLayoutDirection(Qt.RightToLeft if i18n_manager.is_rtl() else Qt.LeftToRight)
        
        self.label_sale.setText(_("label_sale"))
        self.sale_id_input.setPlaceholderText(_("placeholder_search_sale"))
        self.sale_id_input_btn.setText(_("btn_search"))
        
        headers = [
            _("col_product"), _("col_qty_bought"), _("col_unit_price"), 
            _("col_qty_return"), _("col_selection")
        ]
        self.items_table.setHorizontalHeaderLabels(headers)
        
        self.cancel_sale_btn.setText(_("btn_cancel_sale"))
        self.process_return_btn.setText(_("btn_return_selected"))
        self.reprint_btn.setText(_("btn_reprint_ticket"))
        
        if self.sale_data:
            self.display_sale() # Refresh to update any formatted strings if needed
        
    def search_sale(self):
        _ = i18n_manager.get
        term = self.sale_id_input.text().strip()
        if not term:
            return
            
        if term.isdigit():
            sale = pos_manager.get_sale(int(term))
        else:
            QMessageBox.warning(self, "Info", "Recherche par numéro non implémentée")
            return
            
        if sale:
            self.sale_data = sale
            self.display_sale()
        else:
            QMessageBox.warning(self, _("msg_error"), _("msg_sale_not_found"))
            
    def display_sale(self):
        if not self.sale_data:
            return
        
        _ = i18n_manager.get
        self.info_label.setText(_("label_sale_info").format(
            self.sale_data['sale_number'], 
            self.sale_data['total_amount'], 
            self.sale_data['sale_date']
        ))
        
        self.items_table.setRowCount(0)
        items = self.sale_data.get('items', [])
        
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            
            # SpinBox pour quantité retour
            spin = QDoubleSpinBox()
            spin.setRange(0.0, float(item['quantity']))
            spin.setValue(0)
            self.items_table.setCellWidget(row, 3, spin)
            
            # Checkbox
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Unchecked)
            self.items_table.setItem(row, 4, chk)
            
    def cancel_entire_sale(self):
        if not self.sale_data:
            return
        
        _ = i18n_manager.get
        confirm = QMessageBox.question(self, _("confirm_cancel_sale_title"), _("confirm_cancel_sale_msg"), QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            success, msg = pos_manager.cancel_sale(self.sale_data['id'], "Annulation utilisateur")
            if success:
                QMessageBox.information(self, _("msg_success"), msg)
                self.accept()
            else:
                QMessageBox.critical(self, _("msg_error"), msg)
                
    def process_partial_return(self):
        if not self.sale_data:
            return
        
        _ = i18n_manager.get
        items_to_return = []
        rows = self.items_table.rowCount()
        original_items = self.sale_data.get('items', [])
        
        for i in range(rows):
            if self.items_table.item(i, 4).checkState() == Qt.Checked:
                qty = self.items_table.cellWidget(i, 3).value()
                if qty > 0:
                    product_id = original_items[i]['product_id']
                    items_to_return.append({'product_id': product_id, 'quantity': qty})
        
        if not items_to_return:
            QMessageBox.warning(self, "Info", _("msg_no_selection"))
            return
            
        user = auth_manager.get_current_user()
        user_id = user['id'] if user else 1
            
        success, msg, ret_id = pos_manager.process_return(
            self.sale_data['id'], items_to_return, user_id, "Retour partiel"
        )
        
        if success:
            QMessageBox.information(self, _("msg_success"), msg)
            self.accept()
        else:
            QMessageBox.critical(self, _("msg_error"), msg)
            
    def reprint_ticket(self):
        """Réimprimer le ticket de la vente affichée"""
        if not self.sale_data:
            return
            
        printer_manager.print_receipt(self.sale_data, "standard")


class ProductSearchDialog(QDialog):
    """Dialogue de recherche produit pour POS"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_product = None
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        self.setWindowTitle("Recherche Produit")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_product_extended"))
        self.search_input.setMinimumHeight(50)
        self.search_input.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 8px; border: 2px solid #3498db;")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Product Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(_("table_headers_product_search"))
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 14px; }
            QHeaderView::section { background-color: #f0f0f0; padding: 10px; font-weight: bold; }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.cellDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)
        
        # Close Button
        btn_close = QPushButton(_("btn_close"))
        btn_close.setMinimumHeight(40)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.search_input.setFocus()
        self.search_products() # Load empty/all
        
    def search_products(self):
        term = self.search_input.text().strip()
        try:
            if term:
                products = product_manager.search_products(term)
            else:
                return # Don't load all by default or load top 20? 
                # Let's verify behavior. Usually users want to type.
                # If empty, maybe clear table?
                self.table.setRowCount(0)
                return

            self.table.setRowCount(0)
            for p in products:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(p['barcode'] or ""))
                self.table.setItem(row, 1, QTableWidgetItem(p['name']))
                self.table.setItem(row, 2, QTableWidgetItem(f"{p['selling_price']:.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(str(p['stock_quantity'])))
                
                add_btn = QPushButton("Ajouter")
                add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
                add_btn.clicked.connect(lambda ch, prod=p: self.add_product(prod))
                self.table.setCellWidget(row, 4, add_btn)
                
                # Store product data in first item
                self.table.item(row, 0).setData(Qt.UserRole, p)
                
        except Exception as e:
            logger.error(f"Search error: {e}")

    def add_product(self, product):
        # We can emit symbol or call parent method directly if passed
        # Simplest: Emulate POS scan behavior or call add_to_cart
        # Since this is blocking or non-blocking? 
        # User wants "search THERE". So maybe Non-Modal or just re-openable?
        # Implementation: Parent (POS) opens this. This calls parent.add_to_cart(product)
        if self.parent():
            self.parent().add_to_cart(product)
            # Optional: Feedback toast?

    def on_double_click(self, row, col):
        item = self.table.item(row, 0)
        if item:
            product = item.data(Qt.UserRole)
            if product:
                self.add_product(product)

class CustomerSearchDialog(QDialog):
    """Dialogue de recherche client"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_customer = None
        self.customers = []
        self.setup_ui()
        self.load_customers()
        
    def setup_ui(self):
        _ = i18n_manager.get
        self.setWindowTitle("Recherche Client")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un client (Nom, Téléphone)...")
        self.search_input.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 8px; border: 2px solid #3498db;")
        self.search_input.textChanged.connect(self.filter_customers)
        layout.addWidget(self.search_input)
        
        # List (Table)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nom", "Téléphone", "Solde"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 14px; }
            QHeaderView::section { background-color: #f0f0f0; padding: 10px; font-weight: bold; }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.doubleClicked.connect(self.select_customer)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Valider")
        select_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        select_btn.clicked.connect(self.select_customer)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def load_customers(self):
        self.customers = customer_manager.get_all_customers()
        self.update_list(self.customers)
        
    def filter_customers(self, text):
        text = text.lower()
        filtered = [
            c for c in self.customers 
            if text in c['full_name'].lower() or \
               (c['phone'] and text in c['phone'])
        ]
        self.update_list(filtered)
        
    def update_list(self, customers):
        self.table.setRowCount(0)
        for c in customers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(c['full_name']))
            self.table.setItem(row, 1, QTableWidgetItem(c.get('phone', '')))
            self.table.setItem(row, 2, QTableWidgetItem(f"{c.get('current_credit', 0):.2f}"))
            self.table.item(row, 0).setData(Qt.UserRole, c)
            
    def select_customer(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_customer = self.table.item(row, 0).data(Qt.UserRole)
            self.accept()
class POSPage(QWidget):
    """Page Point de Vente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cart = pos_manager.get_cart()
        self.current_customer = None
        self.init_ui()
        
        # Connect to language change
        i18n_manager.language_changed.connect(self.update_ui_text)
        # Connect to data changes for auto-refresh
        data_signals.customers_changed.connect(self.load_customers)
        data_signals.products_changed.connect(self.load_shortcuts)
        data_signals.shortcuts_changed.connect(self.load_shortcuts)
        self.update_ui_text()
        
    def showEvent(self, event):
        """Called when the page is shown"""
        super().showEvent(event)
        # Refresh shortcuts
        if hasattr(self, 'load_shortcuts'):
            self.load_shortcuts()
        # Auto-focus barcode scanner input
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.barcode_input.setFocus())
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for POS"""
        key = event.key()
        
        # Up arrow - select previous cart item
        if key == Qt.Key_Up:
            current_row = self.cart_table.currentRow()
            if current_row > 0:
                self.cart_table.selectRow(current_row - 1)
            event.accept()
            return
        
        # Down arrow - select next cart item
        if key == Qt.Key_Down:
            current_row = self.cart_table.currentRow()
            if current_row < self.cart_table.rowCount() - 1:
                self.cart_table.selectRow(current_row + 1)
            event.accept()
            return
        
        # Number keys 1-9 - set quantity of selected item
        if Qt.Key_1 <= key <= Qt.Key_9:
            # Only if barcode input is NOT focused (to avoid conflicts while typing)
            if not self.barcode_input.hasFocus():
                qty = key - Qt.Key_0  # Convert key to number
                self._update_selected_item_quantity(qty)
                event.accept()
                return
        
        # Key 0 - delete selected item
        if key == Qt.Key_0:
            if not self.barcode_input.hasFocus():
                self._delete_selected_item()
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    def _update_selected_item_quantity(self, qty):
        """Update quantity of currently selected cart item"""
        row = self.cart_table.currentRow()
        if row < 0 or row >= len(self.cart.items):
            return
        
        item = self.cart.items[row]
        item.quantity = qty
        self.update_cart_display()
        # Re-select the same row
        self.cart_table.selectRow(row)
    
    def _delete_selected_item(self):
        """Delete currently selected cart item"""
        row = self.cart_table.currentRow()
        if row < 0 or row >= len(self.cart.items):
            return
        
        item = self.cart.items[row]
        self.cart.remove_item(item.product_id)
        self.update_cart_display()
        
    def update_ui_text(self):
        """Mettre à jour les textes de l'interface"""
        _ = i18n_manager.get
        is_rtl = i18n_manager.is_rtl()
        
        # Layout Direction
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)
        
        # Header
        # Note: These values (0.0) are placeholders, actual values update on cart change
        # We might want to preserve current values if possible, but simplest is to just update format
        # Actually, update_totals() handles the text content usually. 
        # But we need to update the label FORMAT string used in update_totals or just rely on update_totals being called?
        # Let's just update the static parts or trigger a global update. 
        # For now, just setting text might reset it to 0.00 if we don't check.
        # Better: trigger self.update_totals() if it exists? 
        # Yes, `update_totals` exists later in the file (I need to check/verify). 
        # If not, I'll just set the labels.
        # Assuming update_totals will serve the right values later.
        
        # Left Panel
        self.scanner_group.setTitle(_("group_scan"))
        self.barcode_input.setPlaceholderText(_("placeholder_scan"))
        
        if hasattr(self, 'popup_search_btn'):
            self.popup_search_btn.setText(_("btn_search_product") if i18n_manager.get("btn_search_product") != "btn_search_product" else "🔍 Recherche Produit")
        
        self.calc_group.setTitle(_("group_calculator"))
        self.calc_add_btn.setText(_("btn_add_to_cart"))
        
        # Right Panel
        # Right Panel
        # Compact Customer UI uses buttons, no group title to update
        if hasattr(self, 'clear_customer_btn'):
             self.clear_customer_btn.setToolTip("Réinitialiser (Aucun client)") # Static for now or add to i18n if needed

        
        self.cart_label.setText(_("label_cart"))
        self.cart_table.setHorizontalHeaderLabels(_("table_headers_cart"))
        
        self.payment_group.setTitle(_("group_payment"))
        self.print_receipt_cb.setText(_("checkbox_print_ticket"))
        
        # Update Payment Method Items
        current_idx = self.payment_method.currentIndex()
        self.payment_method.setItemText(0, _("payment_cash"))
        self.payment_method.setItemText(1, _("payment_credit"))
        self.payment_method.setCurrentIndex(current_idx)
        
        self.pay_btn.setText(_("btn_pay"))
        self.clear_btn.setText(_("btn_clear_cart"))
        self.discount_btn.setText(_("btn_discount"))
        self.return_btn_pos.setText(_("btn_returns"))
        self.hold_btn.setText(_("btn_hold"))
        self.retrieve_btn.setText(_("btn_retrieve"))

        # Refresh totals display with new currency symbol if any
        self.update_totals()

    def init_ui(self):
        """Initialiser l'interface"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Colonne gauche - Scanner et produits
        self.left_panel_container = self.create_left_panel()
        layout.addWidget(self.left_panel_container, 1) # Equal width
        
        # Colonne droite - Panier et paiement
        self.right_panel_container = self.create_right_panel()
        layout.addWidget(self.right_panel_container, 1) # Equal width
        
        self.setLayout(layout)
        
        # Focus sur le scanner
        self.barcode_input.setFocus()

        # Raccourcis Clavier POS
        QShortcut(QKeySequence("F9"), self, self.process_payment) # F9 pour payer
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.search_input.setFocus()) # Ctrl+F pour recherche
        QShortcut(QKeySequence("Ctrl+Space"), self, lambda: self.barcode_input.setFocus()) # Ctrl+Espace pour scanner
        
        # Overlay Panier en Attente
        self.create_held_cart_overlay()
    
    
    def create_held_cart_overlay(self):
        """Créer l'overlay pour le panier en attente"""
        # Conteneur IN-LAYOUT (plus d'overlay flottant)
        self.held_overlay = QFrame()
        self.held_overlay.setObjectName("heldOverlay")
        self.held_overlay.setStyleSheet("""
            QFrame#heldOverlay {
                background-color: #fff3e0;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        self.held_overlay.hide()
        
        # Layout horizontal
        layout = QHBoxLayout(self.held_overlay)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Label Info
        self.held_info_label = QLabel()
        self.held_info_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #d35400;
        """)
        layout.addWidget(self.held_info_label)
        
        layout.addStretch()
        
        # Bouton Récupérer
        retrieve_btn = QPushButton("🛒 Récupérer")
        retrieve_btn.setCursor(Qt.PointingHandCursor)
        retrieve_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        retrieve_btn.clicked.connect(self.show_held_carts)
        layout.addWidget(retrieve_btn)
        
        # Insert into Right Panel Layout (Index 1 = After Customer, Before Cart)
        if hasattr(self, 'right_panel_container') and self.right_panel_container.layout():
            self.right_panel_container.layout().insertWidget(1, self.held_overlay)
        
        # Initial check
        self.update_held_cart_overlay()

    def update_held_cart_overlay(self):
        """Mettre à jour l'affichage de l'overlay"""
        held_carts = pos_manager.get_held_carts()
        
        if not held_carts:
            self.held_overlay.hide()
            return
            
        count = len(held_carts)
        last_cart = held_carts[-1]
        
        text = f"{count} Panier(s) en attente | Dernier: {last_cart['total']:.2f} DA"
        self.held_info_label.setText(text)
        
        self.held_overlay.show()

    def create_left_panel(self):
        """Créer le panneau gauche"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet("""
            QFrame#leftPanel {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        _ = i18n_manager.get
        
        # En-tête avec TOTAL et Remise (grand)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #6366f1);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 10px;
            }
        """)
        header_layout_inner = QVBoxLayout(header_frame)
        
        # Label TOTAL (très grand)
        self.header_total_label = QLabel(_("label_total").format(0.0))
        self.header_total_label.setStyleSheet("font-size: 38px; font-weight: bold; color: white; background: transparent;")
        header_layout_inner.addWidget(self.header_total_label)
        
        # Label Remise (sous le total)
        self.header_discount_label = QLabel(_("label_discount").format(0.0))
        self.header_discount_label.setStyleSheet("font-size: 16px; color: #fbbf24; background: transparent;")
        header_layout_inner.addWidget(self.header_discount_label)
        
        layout.addWidget(header_frame)
        
        # Scanner code-barres
        self.scanner_group = QGroupBox(_("group_scan"))
        self.scanner_group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 5px;
                padding: 10px 10px 10px 10px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                color: #8b5cf6;
                subcontrol-position: top left;
                padding: 3px 8px;
            }
        """)
        scanner_layout = QVBoxLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText(_("placeholder_scan"))
        self.barcode_input.setMinimumHeight(40)
        self.barcode_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #8b5cf6;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background-color: #faf5ff;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.barcode_input.returnPressed.connect(self.scan_product)
        # Auto-scan après un court délai (pour scanners automatiques)
        self.scan_timer = QTimer()
        self.scan_timer.setSingleShot(True)
        self.scan_timer.timeout.connect(self.auto_scan_product)
        self.barcode_input.textChanged.connect(self.on_barcode_text_changed)
        scanner_layout.addWidget(self.barcode_input)
        self.scanner_group.setLayout(scanner_layout)
        layout.addWidget(self.scanner_group)
        
        # Bouton Recherche Produit (Compressed)
        self.popup_search_btn = QPushButton("🔍 Recherche Produit")
        self.popup_search_btn.setMinimumHeight(45)
        self.popup_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.popup_search_btn.clicked.connect(self.open_search_dialog)
        layout.addWidget(self.popup_search_btn)


        
        # Calculatrice intégrée (Montant Libre) - EN BAS
        self.calc_group = QGroupBox(_("group_calculator"))
        self.calc_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8fff8;
            }
            QGroupBox::title {
                color: #27ae60;
            }
        """)
        calc_layout = QVBoxLayout()
        
        # Écran d'affichage
        self.calc_display = QLineEdit("0")
        self.calc_display.setReadOnly(True)
        self.calc_display.setAlignment(Qt.AlignRight)
        self.calc_display.setMinimumHeight(50)
        self.calc_display.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold;
            padding: 8px; 
            border: 2px solid #27ae60; 
            border-radius: 8px;
            background-color: #e8f5e9;
            color: #2c3e50;
        """)
        calc_layout.addWidget(self.calc_display)
        
        # Grille de boutons
        calc_grid = QGridLayout()
        calc_grid.setSpacing(4)
        
        calc_buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('00', 3, 1), ('C', 3, 2),
        ]
        
        for text, row, col in calc_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            if text == 'C':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #ffcccc; color: #c0392b;")
                btn.clicked.connect(self.calc_clear)
            else:
                btn.clicked.connect(lambda checked, t=text: self.calc_add_digit(t))
            calc_grid.addWidget(btn, row, col)
        
        calc_layout.addLayout(calc_grid)
        
        # Bouton Ajouter au panier
        self.calc_add_btn = QPushButton(_("btn_add_to_cart"))
        self.calc_add_btn.setMinimumHeight(50)
        self.calc_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.calc_add_btn.clicked.connect(self.add_from_calculator)
        calc_layout.addWidget(self.calc_add_btn)
        
        self.calc_group.setLayout(calc_layout)
        layout.addWidget(self.calc_group)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Créer le panneau droit"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet("""
            QFrame#rightPanel {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        _ = i18n_manager.get
        
        # Client - Dropdown Search
        customer_layout = QHBoxLayout()
        
        # Simplified customer search combo
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(45)
        self.customer_combo.setEditable(True)
        self.customer_combo.setInsertPolicy(QComboBox.NoInsert)
        
        # Style
        self.customer_combo.lineEdit().setPlaceholderText("Client de passage / Anonyme")
        self.customer_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 16px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        
        # Populate first (before setting up completer)
        self.load_customers()
        
        # Create a custom completer with string list model for reliable "contains" search
        customer_names = [self.customer_combo.itemText(i) for i in range(self.customer_combo.count())]
        self.customer_completer_model = QStringListModel(customer_names)
        
        self.customer_completer = QCompleter(self.customer_completer_model, self)
        self.customer_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.customer_completer.setFilterMode(Qt.MatchContains)
        self.customer_completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        # Connect completer activation to set the combo box index
        def on_completer_activated(text):
            for i in range(self.customer_combo.count()):
                if self.customer_combo.itemText(i) == text:
                    self.customer_combo.setCurrentIndex(i)
                    break
        
        self.customer_completer.activated.connect(on_completer_activated)
        self.customer_combo.setCompleter(self.customer_completer)
        
        self.customer_combo.setCompleter(self.customer_completer)
        
        # Install event filter for select-all behavior
        self.customer_combo.lineEdit().installEventFilter(self)
        
        self.customer_combo.currentIndexChanged.connect(self.on_customer_selected)

        # Handle text clearing to reset to Anonymous
        def on_text_changed(text):
            if not text.strip():
                self.customer_combo.setCurrentIndex(0) # Reset to Anonyme
                
        self.customer_combo.lineEdit().textChanged.connect(on_text_changed)
        
        customer_layout.addWidget(self.customer_combo, 1) 
        
        # Bouton Recherche Avancée (Nouveau)
        self.search_customer_btn = QPushButton("🔍")
        self.search_customer_btn.setFixedSize(45, 45)
        self.search_customer_btn.setToolTip(_("btn_search"))
        self.search_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0f7fa;
                border: 2px solid #b2ebf2;
                border-radius: 8px;
                font-weight: bold;
                color: #0097a7;
            }
            QPushButton:hover {
                background-color: #b2ebf2;
            }
        """)
        self.search_customer_btn.clicked.connect(self.open_customer_search)
        customer_layout.addWidget(self.search_customer_btn) 
        
        # Bouton Vider sélection
        self.clear_customer_btn = QPushButton("❌")
        self.clear_customer_btn.setFixedSize(45, 45)
        self.clear_customer_btn.setToolTip("Réinitialiser (Aucun client)")
        self.clear_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffebee;
                border: 2px solid #ffcdd2;
                border-radius: 8px;
                font-weight: bold;
                color: #c62828;
            }
            QPushButton:hover {
                background-color: #ffcdd2;
            }
        """)
        self.clear_customer_btn.clicked.connect(self.clear_customer_selection)
        customer_layout.addWidget(self.clear_customer_btn)
        
        layout.addLayout(customer_layout)
        
        # Panier
        self.cart_label = QLabel(_("label_cart"))
        self.cart_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #8b5cf6; margin-top: 10px;")
        layout.addWidget(self.cart_label)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(_("table_headers_cart"))
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.cart_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Removed to allow editing
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: #f3f4f6;
                color: #1a1a2e;
                background-color: #ffffff;
                selection-background-color: #ddd6fe;
                selection-color: #1a1a2e;
                alternate-background-color: #f5f3ff;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #7c3aed;
                padding: 10px;
                font-weight: bold;
                color: #ffffff;
                border: none;
                border-bottom: 2px solid #6d28d9;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #1a1a2e;
            }
            QTableWidget::item:selected {
                background-color: #ddd6fe;
                color: #1a1a2e;
            }
        """)
        self.cart_table.setAlternatingRowColors(True)
        # Enable row selection and keyboard navigation
        self.cart_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cart_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.cart_table.installEventFilter(self)  # For Delete key handling
        # Connecter le signal de changement de cellule pour l'édition de quantité
        self.cart_table.cellChanged.connect(self.on_cart_cell_changed)
        layout.addWidget(self.cart_table)
        
        # Raccourcis POS (Shortcuts Grid)
        shortcuts_label = QLabel("⚡ Raccourcis")
        shortcuts_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #8b5cf6; margin-top: 10px;")
        layout.addWidget(shortcuts_label)
        
        self.shortcuts_container = self.create_shortcuts_grid()
        layout.addWidget(self.shortcuts_container)
        
        # Totaux
        # Totaux supprimés du panneau droit pour laisser plus de place au panier
        # (Déplacés vers le header gauche)
        
        # Paiement
        self.payment_group = QGroupBox(_("group_payment"))
        self.payment_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        payment_layout = QVBoxLayout()
        
        self.payment_method = QComboBox()
        self.payment_method.addItem(_("payment_cash"), "cash")
        self.payment_method.addItem(_("payment_credit"), "credit")
        self.payment_method.setMinimumHeight(40)
        self.payment_method.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                color: #333;
            }
            QComboBox QAbstractItemView {
                color: #333;
            }
        """)
        payment_layout.addWidget(self.payment_method)
        
        # Checkbox pour imprimer le ticket
        self.print_receipt_cb = QCheckBox(_("checkbox_print_ticket"))
        self.print_receipt_cb.setChecked(True)
        self.print_receipt_cb.setStyleSheet("font-size: 14px; padding: 5px;")
        payment_layout.addWidget(self.print_receipt_cb)
        
        self.payment_group.setLayout(payment_layout)
        layout.addWidget(self.payment_group)
        
        # Boutons d'action - Plus gros pour écran tactile
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(12)
        
        # Bouton Payer - TRÈS GRAND pour écran tactile
        self.pay_btn = QPushButton(_("btn_pay"))
        self.pay_btn.setMinimumHeight(80)
        self.pay_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #059669, stop:1 #047857);
            }
            QPushButton:pressed {
                background: #047857;
            }
        """)
        self.pay_btn.clicked.connect(self.process_payment)
        buttons_layout.addWidget(self.pay_btn)
        
        # Boutons secondaires - Plus gros
        secondary_layout = QHBoxLayout()
        secondary_layout.setSpacing(10)
        
        self.clear_btn = QPushButton(_("btn_clear_cart"))
        self.clear_btn.setMinimumHeight(55)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_cart)
        secondary_layout.addWidget(self.clear_btn)

        
        self.discount_btn = QPushButton(_("btn_discount"))
        self.discount_btn.setMinimumHeight(55)
        self.discount_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.discount_btn.clicked.connect(self.apply_discount)
        secondary_layout.addWidget(self.discount_btn)
        
        # Bouton Retour
        self.return_btn_pos = QPushButton(_("btn_returns"))
        self.return_btn_pos.setMinimumHeight(55)
        self.return_btn_pos.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.return_btn_pos.clicked.connect(self.open_returns)
        secondary_layout.addWidget(self.return_btn_pos)
        
        # Bouton En Attente (Hold)
        self.hold_btn = QPushButton(_("btn_hold"))
        self.hold_btn.setMinimumHeight(55)
        self.hold_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.hold_btn.clicked.connect(self.hold_current_cart)
        secondary_layout.addWidget(self.hold_btn)
        
        # Bouton Récupérer (held carts)
        self.retrieve_btn = QPushButton(_("btn_retrieve"))
        self.retrieve_btn.setMinimumHeight(55)
        self.retrieve_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.retrieve_btn.clicked.connect(self.show_held_carts)
        secondary_layout.addWidget(self.retrieve_btn)
        
        buttons_layout.addLayout(secondary_layout)
        layout.addLayout(buttons_layout)
        
        panel.setLayout(layout)
        return panel
    
    def create_shortcuts_grid(self):
        """Créer la grille de raccourcis (Horizontal Scrollable)"""
        from PyQt5.QtWidgets import QScrollArea
        
        # Container principal (Scroll Area)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(115) # Hauteur fixe pour la rangée
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: #fafafa;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: #f0f0f0;
            }
            QScrollBar::handle:horizontal {
                background: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #94a3b8;
            }
        """)
        
        # Container interne pour les boutons
        self.shortcuts_inner_widget = QWidget()
        self.shortcuts_layout = QHBoxLayout(self.shortcuts_inner_widget)
        self.shortcuts_layout.setSpacing(10)
        self.shortcuts_layout.setContentsMargins(10, 10, 10, 10)
        self.shortcuts_layout.setAlignment(Qt.AlignLeft)
        
        # Dictionnaire pour garder une référence aux boutons
        self.shortcut_buttons = {}
        
        scroll_area.setWidget(self.shortcuts_inner_widget)
        
        # Charger les raccourcis
        self.load_shortcuts()
        
        return scroll_area
    
    def create_shortcut_btn(self, position, data=None):
        """Helper pour créer un bouton de raccourci"""
        btn = QPushButton()
        btn.setFixedSize(100, 80)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("position", position)
        
        if data:
            # Raccourci existant
            label = data['label']
            price = data['unit_price']
            btn.setText(f"{label}\n{price:.2f} DA")
            btn.setProperty("shortcut_id", data['id'])
            btn.setProperty("shortcut_id", data['id'])
            btn.setProperty("shortcut_data", data)
            
            # Image
            if data.get('image_path'):
                img_path = Path(data['image_path'])
                if img_path.exists():
                    pixmap = QPixmap(str(img_path))
                    btn.setIcon(QIcon(pixmap))
                    btn.setIconSize(QSize(90, 70)) # Icone plus grande
                    btn.setText("") # Cacher le texte
                    btn.setToolTip(f"{label}\n{price:.2f} DA") # Tooltip garde les infos
                else:
                    btn.setText(f"{label}\n{price:.2f} DA")
            else:
                 btn.setText(f"{label}\n{price:.2f} DA")
            
            # Style actif
            
            # Style actif
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #eff6ff);
                    border: 2px solid #bfdbfe;
                    border-radius: 10px;
                    padding: 5px;
                    font-size: 11px;
                    font-weight: bold;
                    color: #1e40af;
                    text-align: center;
                }
                QPushButton:hover {
                    background: #dbeafe;
                    border-color: #3b82f6;
                }
                QPushButton:pressed {
                    background: #bfdbfe;
                }
            """)
        else:
            # Case vide - Ne rien afficher ou un placeholder inactif
            btn.setText("")
            btn.setEnabled(False)
            btn.setStyleSheet("border: none; background: transparent;")
            return btn # Retourner bouton invisible pour maintenir layout si nécessaire, ou on pourrait ne rien retourner
            
        # Connexions
        btn.clicked.connect(lambda checked, pos=position: self.on_shortcut_clicked(pos))
        
        # Context menu
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda point, pos=position: self.show_shortcut_context_menu(pos, btn.mapToGlobal(point))
        )
        
        return btn

    def load_shortcuts(self):
        """Charger et afficher les raccourcis"""
        try:
            # Nettoyer le layout existant
            while self.shortcuts_layout.count():
                item = self.shortcuts_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            self.shortcut_buttons = {}
            
            # Récupérer les raccourcis de la BDD
            shortcuts = shortcuts_manager.get_all_shortcuts()
            # Convertir en dictionnaire par position pour accès facile
            shortcuts_map = {s['position']: s for s in shortcuts}
            
            # Déterminer le nombre de slots à afficher
            # Au moins 6, ou le max position + 1 si > 6 (pour laisser un slot vide à la fin)
            max_pos = max(shortcuts_map.keys()) if shortcuts_map else 0
            num_slots = max(6, max_pos + 1)
            # Limite max raisonnable (ex: 20)
            num_slots = min(num_slots, 20)
            
            # Créer les boutons
            for i in range(num_slots):
                position = i + 1
                data = shortcuts_map.get(position)
                
                btn = self.create_shortcut_btn(position, data)
                self.shortcuts_layout.addWidget(btn)
                self.shortcut_buttons[position] = btn
                
            self.shortcuts_layout.addStretch()
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des raccourcis: {e}")
    
    def on_shortcut_clicked(self, position):
        """Gérer le clic sur un raccourci"""
        btn = self.shortcut_buttons.get(position)
        if not btn:
            return
        
        shortcut_id = btn.property("shortcut_id")
        shortcut_data = btn.property("shortcut_data")
        
        if shortcut_id:
            # Raccourci existant - demander la quantité
            self.use_shortcut(shortcut_data)
        else:
            # Ne rien faire pour les emplacements vides (ou ne plus avoir de tels boutons)
            pass
    
    def use_shortcut(self, shortcut_data):
        """Utiliser un raccourci pour ajouter au panier"""
        from PyQt5.QtWidgets import QInputDialog
        
        label = shortcut_data['label']
        unit_price = shortcut_data['unit_price']
        
        # Demander la quantité
        quantity, ok = QInputDialog.getDouble(
            self,
            "Quantité",
            f"{label}\nPrix unitaire: {unit_price:.2f} DA\n\nCombien ?",
            1.0,  # Valeur par défaut
            0.1,  # Minimum
            9999,  # Maximum
            1     # Décimales
        )
        
        if ok and quantity > 0:
            # Créer un pseudo-produit pour l'ajouter au panier
            if shortcut_data['product_id']:
                # Produit existant
                try:
                    product = product_manager.get_product(shortcut_data['product_id'])
                    if product:
                        # Utiliser le prix du raccourci au lieu du prix du produit
                        product['selling_price'] = unit_price
                        success, message = self.cart.add_item(product, quantity)
                        
                        if success:
                            self.update_cart_display()
                            logger.info(f"Raccourci utilisé: {label} x{quantity}")
                        else:
                            QMessageBox.warning(self, "Erreur", message)
                    else:
                        QMessageBox.warning(self, "Erreur", "Produit introuvable")
                except Exception as e:
                    logger.error(f"Erreur utilisation raccourci: {e}")
                    QMessageBox.critical(self, "Erreur", str(e))
            else:
                # Produit personnalisé (pas encore dans la base ou custom)
                # On utilise add_to_cart avec product_id=0 pour utiliser la logique du produit Divers
                # Mais il faut passer category_id qui n'est pas supporté directement par add_to_cart actuel
                # On va donc construire l'objet produit manuellement et appeler self.cart.add_item
                
                custom_product = {
                    'id': 0, # Marquer comme custom
                    'name': label,
                    'barcode': None,
                    'selling_price': unit_price,
                    'purchase_price': 0,
                    'stock_quantity': 9999,
                    'category_id': shortcut_data.get('category_id') # New: Pass category
                }
                
                # Prevent merge pour les items custom pour garder distincts si besoin, ou on merge par nom/prix
                success, message = self.cart.add_item(custom_product, quantity, prevent_merge=False)
                
                if success:
                    self.update_cart_display()
                    logger.info(f"Raccourci personnalisé utilisé: {label} x{quantity}")
                else:
                    QMessageBox.warning(self, "Erreur", message)
    
    def show_shortcut_context_menu(self, position, global_pos):
        """Afficher le menu contextuel pour un raccourci"""
        from PyQt5.QtWidgets import QMenu
        
        btn = self.shortcut_buttons.get(position)
        if not btn:
            return
        
        shortcut_id = btn.property("shortcut_id")
        
        if not shortcut_id:
            # Pas de menu pour les emplacements vides
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Modifier")
        delete_action = menu.addAction("🗑 Supprimer")
        
        action = menu.exec_(global_pos)
        
        if action == edit_action:
            self.open_shortcut_config(shortcut_id=shortcut_id)
        elif action == delete_action:
            # Confirmation de suppression
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Êtes-vous sûr de vouloir supprimer ce raccourci ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, msg = shortcuts_manager.delete_shortcut(shortcut_id)
                if success:
                    self.load_shortcuts()
                    QMessageBox.information(self, "Succès", msg)
                else:
                    QMessageBox.warning(self, "Erreur", msg)
    
    def open_shortcut_config(self, shortcut_id=None, position=None):
        """Ouvrir le dialogue de configuration de raccourci"""
        dialog = ShortcutConfigDialog(shortcut_id=shortcut_id, position=position, parent=self)
        
        if dialog.exec_() == QDialog.Accepted:
            # Recharger les raccourcis
            self.load_shortcuts()
    
    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre"""
        if is_dark:
            # Mode sombre
            main_bg = "#2c3e50"
            panel_bg = "#34495e"
            text_color = "white"
            input_bg = "#2c3e50"
            
            self.left_panel_container.setStyleSheet(f"""
                QFrame#leftPanel {{
                    background-color: {panel_bg};
                    border-radius: 10px;
                    padding: 15px;
                    color: {text_color};
                }}
            """)
            
            self.right_panel_container.setStyleSheet(f"""
                QFrame#rightPanel {{
                    background-color: {panel_bg};
                    border-radius: 10px;
                    padding: 15px;
                    color: {text_color};
                }}
            """)
            
            # Mise à jour des tables
            table_style = f"""
                QTableWidget {{
                    border: 2px solid #555;
                    border-radius: 8px;
                    background-color: #2c3e50;
                    gridline-color: #555;
                    color: white;
                }}
                QHeaderView::section {{
                    background-color: #455a64;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                    color: white;
                }}
            """
            self.products_table.setStyleSheet(table_style)
            self.cart_table.setStyleSheet(table_style)
            
            # Mise à jour des inputs
            input_style = f"""
                QLineEdit {{
                    padding: 10px 15px;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    font-size: 16px;
                    background-color: #2c3e50;
                    color: white;
                }}
            """
            self.barcode_input.setStyleSheet(input_style)
            self.search_input.setStyleSheet(input_style.replace("16px", "14px").replace("#667eea", "white"))
            
            # ComboBoxes
            combo_style = """
                QComboBox {
                    padding: 8px 12px;
                    border: 2px solid #555;
                    border-radius: 6px;
                    font-size: 14px;
                    color: white;
                    background-color: #2c3e50;
                }
                QComboBox QAbstractItemView {
                    background-color: #2c3e50;
                    color: white;
                    selection-background-color: #667eea;
                }
            """
            self.customer_combo.setStyleSheet(combo_style)
            self.payment_method.setStyleSheet(combo_style)
            
            if hasattr(self, 'clear_customer_btn'):
                self.clear_customer_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #34495e;
                        border: 1px solid #555;
                        border-radius: 8px;
                        font-weight: bold;
                        color: #ecf0f1;
                    }
                    QPushButton:hover {
                        background-color: #4a6785;
                        color: #e74c3c;
                    }
                """)
            
        else:
            # Mode clair (reset aux styles d'origine)
            self.left_panel_container.setStyleSheet("""
                QFrame#leftPanel {
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            self.right_panel_container.setStyleSheet("""
                QFrame#rightPanel {
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            
            # Tables
            table_style = """
                QTableWidget {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #f0f0f0;
                    color: #333;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                    color: #333;
                }
            """
            self.products_table.setStyleSheet(table_style)
            self.cart_table.setStyleSheet(table_style)
            
            # Inputs
            input_style = """
                QLineEdit {
                    padding: 10px 15px;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    font-size: 16px;
                    background-color: #f0f4ff;
                    color: #333;
                }
            """
            self.barcode_input.setStyleSheet(input_style)
            
            # Combo
            combo_style = """
                QComboBox {
                    padding: 8px 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    font-size: 14px;
                    color: #333;
                }
            """
            self.customer_combo.setStyleSheet(combo_style)
            self.payment_method.setStyleSheet(combo_style)
            
            if hasattr(self, 'clear_customer_btn'):
                self.clear_customer_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        color: #555;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                        color: #e74c3c;
                    }
                """)

    def load_customers(self):
        """Charger la liste des clients"""
        try:
            self.customer_combo.blockSignals(True)
            self.customer_combo.clear()
            
            # Add default Anonymous/Walk-in client
            self.customer_combo.addItem("Client de passage / Anonyme", None)
            
            customers = customer_manager.get_all_customers()
            for customer in customers:
                display_name = f"{customer['full_name']} ({customer['code']})"
                self.customer_combo.addItem(display_name, customer)
            
            # Select default (Anonyme)
            self.customer_combo.setCurrentIndex(0)
            
            self.customer_combo.blockSignals(False)
        except Exception as e:
            logger.error(f"Erreur chargement clients: {e}")
            self.customer_combo.blockSignals(False)
            
    def open_customer_search(self):
        """Ouvrir le dialogue de recherche client"""
        dialog = CustomerSearchDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            selected = dialog.selected_customer
            if selected:
                # Find customer by ID in combo box (data is stored as dict)
                selected_id = selected['id']
                found_idx = -1
                
                for i in range(self.customer_combo.count()):
                    customer_data = self.customer_combo.itemData(i)
                    if customer_data and customer_data.get('id') == selected_id:
                        found_idx = i
                        break
                
                if found_idx >= 0:
                    self.customer_combo.setCurrentIndex(found_idx)
                else:
                    # Customer not in list, reload and try again
                    self.load_customers()
                    for i in range(self.customer_combo.count()):
                        customer_data = self.customer_combo.itemData(i)
                        if customer_data and customer_data.get('id') == selected_id:
                            self.customer_combo.setCurrentIndex(i)
                            break


    def scan_product(self):
        """Scanner un produit par code-barres - ajoute directement au panier"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        try:
            product = product_manager.get_product_by_barcode(barcode)
            if product:
                # Add directly with quantity 1, no popup
                self.add_to_cart(product, quantity=1, ask_quantity=False)
                self.barcode_input.clear()
            else:
                # Check if input is numeric (quantity update for selected item)
                if barcode.isdigit():
                    qty = int(barcode)
                    if qty > 0:
                        self._update_selected_item_quantity(qty)
                        self.barcode_input.clear()
                    else:
                        # qty=0 means delete
                        self._delete_selected_item()
                        self.barcode_input.clear()
                else:
                    QMessageBox.warning(self, "❌ Produit n'existe pas", 
                                      f"Le produit avec le code-barres\n"
                                      f"'{barcode}'\n"
                                      f"n'existe pas dans la liste des produits.\n\n"
                                      f"Vérifiez le code-barres ou ajoutez le produit.")
                    self.barcode_input.clear()
        except Exception as e:
            logger.error(f"Erreur scan produit: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du scan: {e}")
        finally:
            # Always refocus the barcode input for continuous scanning
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, lambda: self.barcode_input.setFocus())
    
    def on_barcode_text_changed(self, text):
        """Démarrer le timer pour auto-scan"""
        if text.strip():
            # Redémarrer le timer à chaque frappe
            self.scan_timer.start(300)  # 300ms délai
        else:
            self.scan_timer.stop()
    
    def auto_scan_product(self):
        """Auto-scan du produit après délai"""
        barcode = self.barcode_input.text().strip()
        if barcode and len(barcode) >= 3:  # Au moins 3 caractères
            self.scan_product()
    
    def search_products(self):
        """Rechercher des produits"""
        search_term = self.search_input.text().strip()
        
        try:
            products = product_manager.search_products(search_term) if search_term else []
            self.display_products(products)
        except Exception as e:
            logger.error(f"Erreur recherche produits: {e}")
    
    def display_products(self, products):
        """Afficher les produits trouvés"""
        self.products_table.setRowCount(0)
        self.last_search_results = products  # Stocker pour double-click
        
        for i, product in enumerate(products):
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            
            self.products_table.setItem(row, 0, QTableWidgetItem(product['barcode'] or ''))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(f"{product['selling_price']:.2f} DA"))
            item_stock = QTableWidgetItem(str(product['stock_quantity']))
            if product['stock_quantity'] <= product['min_stock_level']:
                 item_stock.setForeground(QColor("red"))
            self.products_table.setItem(row, 3, item_stock)
            
            # Bouton Ajouter
            add_btn = QPushButton("➕ Ajouter")
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            self.products_table.setCellWidget(row, 4, add_btn)

    def on_product_double_click(self, row, column):
        """Ajouter au panier sur double click"""
        if hasattr(self, 'last_search_results') and 0 <= row < len(self.last_search_results):
            product = self.last_search_results[row]
            self.add_to_cart(product)

    def add_to_cart(self, product, quantity=1.0, ask_quantity=True):
        """Ajouter un produit au panier
        
        Args:
            product: Product dict
            quantity: Default quantity (used when ask_quantity=False)
            ask_quantity: If True, show popup to ask quantity. If False, use provided quantity directly.
        """
        try:
            _ = i18n_manager.get
            qty = quantity
            
            if ask_quantity:
                # Demander la quantité
                qty, ok = QInputDialog.getDouble(
                    self, 
                    _("label_quantity"),  # "Quantité"
                    f"{product['name']}\n{_('label_enter_quantity')}:", # "Entrez la quantité :"
                    1.0,  # Valeur par défaut
                    0.01, # Minimum
                    9999, # Maximum
                    2     # Décimales
                )
                
                if not ok:
                    return

            success, message = self.cart.add_item(product, qty)
            
            if success:
                self.update_cart_display()
                logger.info(f"Produit ajouté au panier: {product['name']} x{qty}")
                
                # Auto-select the last row (most recently added item)
                row_count = self.cart_table.rowCount()
                if row_count > 0:
                    self.cart_table.selectRow(row_count - 1)
            else:
                logger.warning(f"Échec ajout panier ({product['name']}): {message}")
                QMessageBox.warning(self, _("title_warning"), message)
                
        except Exception as e:
            logger.error(f"Erreur ajout panier: {e}")
            _ = i18n_manager.get
            QMessageBox.critical(self, _("title_error"), f"{_('system_error').format(e)}")

    
    def update_cart_display(self):
        """Mettre à jour l'affichage du panier"""
        self.cart_table.blockSignals(True)  # Empêcher les boucles infinies
        self.cart_table.setRowCount(0)
        
        for item in self.cart.items:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            
            self.cart_table.setItem(row, 0, QTableWidgetItem(item.product_name))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item.unit_price:.2f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item.get_subtotal():.2f}"))
            
            # Bouton supprimer
            remove_btn = QPushButton("❌")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
            """)
            remove_btn.clicked.connect(lambda checked, pid=item.product_id: self.remove_from_cart(pid))
            self.cart_table.setCellWidget(row, 4, remove_btn)
        
        # Mettre à jour les totaux (dans le header gauche)
        discount = self.cart.get_discount_amount()
        total = self.cart.get_total()
        
        _ = i18n_manager.get
        self.header_discount_label.setText(_("label_discount").format(discount))
        self.header_total_label.setText(_("label_total").format(total))
        
        self.cart_table.blockSignals(False)  # Réactiver les signaux
        
        # Auto-select the last row (most recently added item)
        row_count = self.cart_table.rowCount()
        if row_count > 0:
            self.cart_table.selectRow(row_count - 1)
            # Don't steal focus from barcode input - keep scanner ready
            if not self.barcode_input.hasFocus():
                self.barcode_input.setFocus()
    
    def remove_from_cart(self, product_id):
        """Retirer un produit du panier"""
        self.cart.remove_item(product_id)
        self.update_cart_display()
    
    


    def on_customer_selected(self, index):
        """Gérer la sélection d'un client"""
        if index < 0:
            self.current_customer = None
        else:
            self.current_customer = self.customer_combo.itemData(index)
    
    def set_customer(self, customer_data):
        """Définir le client actuel (depuis Panier Récupéré)"""
        if not customer_data:
            self.clear_customer_selection()
            return
            
        # Find index by ID
        cust_id = customer_data.get('id')
        for i in range(self.customer_combo.count()):
            data = self.customer_combo.itemData(i)
            if data and data.get('id') == cust_id:
                self.customer_combo.setCurrentIndex(i)
                # self.current_customer is set by signal handler
                return
        
        self.clear_customer_selection()

    def clear_customer_selection(self):
        """Réinitialiser la sélection client"""
        if hasattr(self, 'customer_combo'):
            self.customer_combo.setCurrentIndex(0)
        self.current_customer = None
    
    def clear_cart(self):
        """Vider le panier"""
        _ = i18n_manager.get
        reply = QMessageBox.question(
            self, _("msg_confirm_clear_title", "Confirmation"),
            _("msg_confirm_clear"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart.clear()
            self.update_cart_display()
    
    def apply_discount(self):
        """Appliquer une remise"""
        _ = i18n_manager.get
        discount, ok = QInputDialog.getDouble(
            self, _("btn_discount"),
            "Montant de la remise (DA):",
            0, 0, 100000, 2
        )
        
        if ok:
            success, message = self.cart.set_discount_amount(discount)
            if success:
                self.update_cart_display()
            else:
                QMessageBox.warning(self, _("title_error"), message)
                
    def open_returns(self):
        """Ouvrir le dialogue de retours"""
        dialog = ReturnDialog(self)
        dialog.exec_()
    
    def hold_current_cart(self):
        """Mettre le panier actuel en attente"""
        _ = i18n_manager.get
        if self.cart.is_empty():
            QMessageBox.warning(self, _("title_warning"), _("msg_cart_empty"))
            return
        
        # Automatically determine name without prompt
        name = ""
        customer_data = None
        
        if self.current_customer:
            # Assuming 'full_name' or 'name' exists
            name = self.current_customer.get('full_name', self.current_customer.get('name', 'Client'))
            customer_data = self.current_customer
        
        success, msg = pos_manager.hold_cart(name, customer_data=customer_data)
        if success:
            self.cart = pos_manager.get_cart()
            # Reset current customer since we start a new cart
            self.current_customer = None
            self.clear_customer_selection()
            
            self.update_cart_display()
            # Update visual overlay
            self.update_held_cart_overlay()
            QMessageBox.information(self, _("title_success"), msg)
        else:
            QMessageBox.warning(self, _("title_error"), msg)
    
    def show_held_carts(self):
        """Afficher les paniers en attente"""
        _ = i18n_manager.get
        held_carts = pos_manager.get_held_carts()
        
        if not held_carts:
            QMessageBox.information(self, _("title_info"), _("msg_no_held_carts"))
            return
        
        # Create dialog to show held carts
        dialog = QDialog(self)
        dialog.setWindowTitle(_("title_held_carts"))
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # List
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([_("col_id"), _("col_customer"), _("col_total"), _("col_time")])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        table.setRowCount(len(held_carts))
        for i, cart_data in enumerate(held_carts):
            table.setItem(i, 0, QTableWidgetItem(str(cart_data['id'])))
            table.setItem(i, 1, QTableWidgetItem(cart_data['customer_name']))
            table.setItem(i, 2, QTableWidgetItem(f"{cart_data['total']:.2f}"))
            time_str = cart_data['timestamp'].strftime("%H:%M")
            table.setItem(i, 3, QTableWidgetItem(time_str))
            # Store ID
            table.item(i, 0).setData(Qt.UserRole, cart_data['id'])
            
        layout.addWidget(table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        retrieve_btn = QPushButton(_("btn_retrieve"))
        retrieve_btn.setStyleSheet("background-color: #27ae60; color: white;")
        retrieve_btn.clicked.connect(lambda: self._retrieve_selected_cart(dialog, table))
        
        delete_btn = QPushButton(_("btn_delete"))
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        delete_btn.clicked.connect(lambda: self._delete_selected_cart(dialog, table))
        
        close_btn = QPushButton(_("btn_close"))
        close_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(retrieve_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
        
    def _retrieve_selected_cart(self, dialog, table):
        """Récupérer le panier sélectionné"""
        _ = i18n_manager.get
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(dialog, _("title_warning"), _("msg_select_cart"))
            return
            
        cart_id = table.item(current_row, 0).data(Qt.UserRole)
        
        # Pass current customer to save it with the swapped cart
        success, msg, retrieved_customer = pos_manager.retrieve_cart(cart_id, self.current_customer)
        
        if success:
            self.cart = pos_manager.get_cart()
            self.update_cart_display()
            self.update_held_cart_overlay() # Update overlay
            
            # Restore customer
            # Restore customer
            if retrieved_customer:
                self.set_customer(retrieved_customer)
            else:
                self.clear_customer_selection()
            
            dialog.accept()
        else:
            QMessageBox.warning(dialog, _("title_error"), msg)
            
    def _delete_selected_cart(self, dialog, table):
        """Supprimer le panier sélectionné"""
        _ = i18n_manager.get
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(dialog, _("title_warning"), _("msg_select_cart"))
            return
            
        cart_id = table.item(current_row, 0).data(Qt.UserRole)
        confirm = QMessageBox.question(dialog, _("title_confirm"), _("msg_confirm_delete"), 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = pos_manager.delete_held_cart(cart_id)
            if success:
                # Refresh list by closing and reopening? Or remove row?
                # Removing row is cleaner
                table.removeRow(current_row)
                self.update_held_cart_overlay() # Update overlay count
            else:
                QMessageBox.warning(dialog, _("title_error"), msg)

        




    def on_cart_cell_changed(self, row, column):
        """Gérer la modification directe dans le panier (Quantité)"""
        # ... logic ...
        # (Content omitted for brevity/safety, verify indentation if inserting)
        # Assuming we append this new method at end:
        pass # Placeholder for existing method body if not fully visible

    def open_search_dialog(self):
        """Ouvrir le dialogue de recherche produit"""
        dialog = ProductSearchDialog(self)
        dialog.exec_()
    
    def on_cart_cell_changed(self, row, column):
        """Gérer la modification directe dans le panier (Quantité)"""
        # Colonne 2 = Quantité
        if column != 2:
            return
            
        try:
            qty_item = self.cart_table.item(row, column)
            if not qty_item:
                return
                
            new_qty_str = qty_item.text()
            try:
                new_qty = float(new_qty_str)
            except ValueError:
                return # Ignorer si pas un nombre
            
            if row < len(self.cart.items):
                item = self.cart.items[row]
                
                # Mettre à jour si différent
                if item.quantity != new_qty:
                    success, msg = self.cart.update_quantity(item.product_id, new_qty)
                    if success:
                        # Rafraichir l'affichage pour mettre à jour les sous-totaux et totaux
                        # Note: update_cart_display bloque les signaux, donc pas de boucle
                        self.update_cart_display()
                    else:
                        # Revert value if failed (e.g. stock)
                        self.cart_table.blockSignals(True)
                        qty_item.setText(str(item.quantity))
                        self.cart_table.blockSignals(False)
                        QMessageBox.warning(self, "Attention", msg)
                        
        except Exception as e:
            logger.error(f"Erreur edition panier: {e}")
        

    
    def add_custom_product(self):
        """Ajouter un produit personnalisé (non référencé dans la base)"""
        _ = i18n_manager.get
        dialog = QDialog(self)
        dialog.setWindowTitle(_("custom_product_title"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Champs
        name_input = QLineEdit()
        name_input.setPlaceholderText(_("placeholder_product_name"))
        name_input.setMinimumHeight(40)
        
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 999999)
        price_input.setDecimals(2)
        price_input.setSuffix(" DA")
        price_input.setMinimumHeight(40)
        price_input.setStyleSheet("font-size: 16px;")
        
        qty_input = QDoubleSpinBox()
        qty_input.setRange(0.01, 1000)
        qty_input.setValue(1)
        qty_input.setMinimumHeight(40)
        
        form.addRow(_("label_product_name"), name_input)
        form.addRow(_("label_unit_price"), price_input)
        form.addRow(_("label_quantity"), qty_input)
        
        layout.addLayout(form)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(_("btn_add_to_cart"))
        add_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold;")
        add_btn.setMinimumHeight(50)
        
        cancel_btn = QPushButton(_("btn_cancel"))
        cancel_btn.setMinimumHeight(50)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        def add_to_cart():
            name = name_input.text().strip()
            price = price_input.value()
            qty = qty_input.value()
            
            if not name:
                QMessageBox.warning(dialog, _("title_error"), _("msg_enter_product_name"))
                return
            if price <= 0:
                QMessageBox.warning(dialog, _("title_error"), _("msg_valid_price"))
                return
            
            # Créer un produit temporaire (non sauvegardé en base)
            custom_product = {
                'id': -1,  # ID négatif pour indiquer produit personnalisé
                'barcode': f"CUSTOM-{datetime.now().strftime('%H%M%S')}",
                'name': name,
                'selling_price': price,
                'purchase_price': 0,
                'stock_quantity': 999  # Stock illimité pour produit personnalisé
            }
            
            success, msg = self.cart.add_item(custom_product, qty)
            if success:
                self.update_cart_display()
                dialog.accept()
                QMessageBox.information(self, _("title_success"), _("msg_added_to_cart").format(name, qty))
            else:
                QMessageBox.warning(dialog, _("title_error"), msg)
        
        add_btn.clicked.connect(add_to_cart)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def process_payment(self):
        """Traiter le paiement"""
        _ = i18n_manager.get
        # Check explicitement si items est vide
        if not self.cart.items:
            # Reusing msg_cart_empty_pay or similar
            QMessageBox.warning(self, _("title_warning"), _("msg_cart_empty_pay"))
            return
        
        try:
            customer_data = self.customer_combo.currentData()
            customer_id = customer_data['id'] if isinstance(customer_data, dict) else customer_data
            
            payment_method = self.payment_method.currentData()
            
            # Vérifier si crédit est sélectionné mais pas de client
            if payment_method == 'credit' and not customer_id:
                QMessageBox.warning(self, _("title_warning"), 
                    _("msg_client_required_credit"))
                return

            total = self.cart.get_total()
            credit_amount = 0
            
            # Logic for CREDIT payment: Ask if there is an initial payment
            if payment_method == 'credit':
                # Custom dialog for partial payment
                dialog = QDialog(self)
                dialog.setWindowTitle(_("dialog_credit_details_title"))
                dialog.setFixedSize(400, 250)
                dialog.setStyleSheet("background-color: white;")
                
                layout = QVBoxLayout(dialog)
                
                # Title
                title = QLabel(_("label_total_to_pay").format(total))
                title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
                title.setAlignment(Qt.AlignCenter)
                layout.addWidget(title)
                
                # Input for cash paid
                input_layout = QFormLayout()
                amount_paid_spin = QDoubleSpinBox()
                amount_paid_spin.setRange(0, total)
                amount_paid_spin.setDecimals(2)
                amount_paid_spin.setSuffix(" " + _("currency", "DA"))
                amount_paid_spin.setValue(0) # Default to 0 for credit
                amount_paid_spin.setStyleSheet("""
                    QDoubleSpinBox {
                        font-size: 16px; padding: 8px; border: 2px solid #3498db; border-radius: 6px;
                    }
                """)
                input_layout.addRow(_("label_cash_paid_now"), amount_paid_spin)
                layout.addLayout(input_layout)
                
                # Remaining credit label
                remaining_label = QLabel(_("label_remaining_credit").format(total))
                remaining_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c; margin-top: 10px;")
                remaining_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(remaining_label)
                
                def update_remaining():
                    paid = amount_paid_spin.value()
                    rem = total - paid
                    remaining_label.setText(_("label_remaining_credit").format(rem))
                    if rem == 0:
                        remaining_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
                        remaining_label.setText(_("label_payment_complete"))
                    else:
                        remaining_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
                
                amount_paid_spin.valueChanged.connect(update_remaining)
                
                # Buttons
                btn_layout = QHBoxLayout()
                cancel_btn = QPushButton(_("btn_cancel"))
                cancel_btn.clicked.connect(dialog.reject)
                validate_btn = QPushButton(_("btn_validate_payment"))
                validate_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71; color: white; font-weight: bold; padding: 10px; border-radius: 6px;
                    }
                    QPushButton:hover { background-color: #27ae60; }
                """)
                validate_btn.clicked.connect(dialog.accept)
                
                btn_layout.addWidget(cancel_btn)
                btn_layout.addWidget(validate_btn)
                layout.addLayout(btn_layout)
                
                if dialog.exec_() == QDialog.Accepted:
                    amount_paid = amount_paid_spin.value()
                    credit_amount = total - amount_paid
                    
                    if amount_paid > 0 and credit_amount > 0:
                        payment_method = 'mixed'
                    elif credit_amount == 0:
                        payment_method = 'cash'
                    # else stays 'credit'
                else:
                    return # Cancelled
            
            # ===== CREDIT LIMIT CHECK =====
            # (Use calculated credit_amount for check)
            check_amount = credit_amount if payment_method in ('credit', 'mixed') else 0
            
            if check_amount > 0 and customer_id:
                customer = customer_manager.get_customer(customer_id)
                if customer:
                    current_credit = float(customer.get('current_credit', 0) or 0)
                    credit_limit = float(customer.get('credit_limit', 0) or 0)
                    new_credit = current_credit + check_amount
                    
                    if credit_limit > 0 and new_credit > credit_limit:
                        # Check if user has override permission
                        can_override = auth_manager.has_permission('override_credit_limit')
                        
                        if not can_override:
                            QMessageBox.critical(self, _("msg_credit_limit_exceeded"), 
                                _("msg_credit_limit_details").format(credit_limit, current_credit, check_amount, new_credit))
                            return
                        else:
                            # Admin can override - show warning and confirm
                            confirm = QMessageBox.warning(self, _("msg_override_credit"),
                                _("msg_override_credit_details").format(credit_limit, new_credit),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm != QMessageBox.Yes:
                                return
            # ===== END CREDIT LIMIT CHECK =====
            
            # Obtenir l'utilisateur actuel (caissier)
            current_user = auth_manager.get_current_user()
            cashier_id = current_user['id'] if current_user else 1
            
            # Pass credit_amount to complete_sale for partial payment handling
            success, message, sale_id = pos_manager.complete_sale(
                cashier_id,
                payment_method,
                total,
                customer_id,
                credit_amount=credit_amount if payment_method in ('credit', 'mixed') else None
            )
            
            if success:
                # Rafraîchir la référence du panier (car recréé dans POSManager)
                self.cart = pos_manager.get_cart()
                self.update_cart_display()
                
                # Réinitialiser champs
                self.customer_combo.setCurrentIndex(-1)
                self.customer_combo.lineEdit().clear()
                self.payment_method.setCurrentIndex(0)
                
                # Afficher l'aperçu du ticket SEULEMENT si checkbox cochée
                if self.print_receipt_cb.isChecked():
                    sale_data = pos_manager.get_sale(sale_id)
                    if sale_data:
                        # Impression directe et silencieuse selon les paramètres
                        from modules.sales.printer import printer_manager
                        printer_manager.print_receipt(sale_data)
                
                # Toujours afficher le message de succès
                QMessageBox.information(self, _("title_success"), 
                    _("msg_sale_recorded").format(sale_id))
                
            else:
                QMessageBox.warning(self, _("title_error"), message)
                
        except Exception as e:
            logger.error(f"Erreur paiement: {e}")
            QMessageBox.critical(self, _("title_error"), f"{_('system_error').format(e)}")

    def update_totals(self):
        """Mettre à jour les totaux"""
        _ = i18n_manager.get
        discount = self.cart.get_discount_amount()
        total = self.cart.get_total()
        
        self.header_discount_label.setText(_("label_discount").format(discount))
        self.header_total_label.setText(_("label_total").format(total))

    def refresh(self):
        """Rafraîchir les données de la page"""
        self.update_ui_text() 
        self.load_customers()
        self.load_shortcuts()
        
    def eventFilter(self, source, event):
        """Filters events for customer combo and cart table keyboard navigation"""
        # Handle Delete key on cart table
        if hasattr(self, 'cart_table') and source == self.cart_table:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Delete:
                    current_row = self.cart_table.currentRow()
                    if current_row >= 0 and current_row < len(self.cart.items):
                        product_id = self.cart.items[current_row].product_id
                        self.remove_from_cart(product_id)
                        # Re-select a row after deletion
                        new_row_count = self.cart_table.rowCount()
                        if new_row_count > 0:
                            select_row = min(current_row, new_row_count - 1)
                            self.cart_table.selectRow(select_row)
                        return True  # Event handled
        
        # Handle customer combo auto-select
        if hasattr(self, 'customer_combo') and source == self.customer_combo.lineEdit():
            if event.type() == QEvent.FocusIn or event.type() == QEvent.MouseButtonPress:
                QTimer.singleShot(0, self.customer_combo.lineEdit().selectAll)
        
        return super().eventFilter(source, event)

    def calc_add_digit(self, digit):
        """Ajouter un chiffre à la calculatrice"""
        current = self.calc_display.text()
        if current == "0":
            self.calc_display.setText(digit)
        else:
            self.calc_display.setText(current + digit)
    
    def calc_clear(self):
        """Effacer la calculatrice"""
        self.calc_display.setText("0")
    
    def add_from_calculator(self):
        """Ajouter le montant de la calculatrice au panier"""
        _ = i18n_manager.get
        try:
            price = int(self.calc_display.text())
        except:
            price = 0
            
        if price <= 0:
            QMessageBox.warning(self, _("title_warning"), _("msg_amount_positive"))
            return
            
        success, msg = pos_manager.add_to_cart(
            product_id=0,
            quantity=1,
            custom_price=price,
            product_name=_("product_misc")
        )
        
        if success:
            self.calc_display.setText("0")
            self.update_cart_display()
        else:
            QMessageBox.warning(self, _("title_error"), msg)
            

class CalculatorDialog(QDialog):
    """Dialogue Calculatrice Simple"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculatrice")
        self.setFixedSize(300, 400)
        self.layout = QVBoxLayout()
        
        # Écran
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(50)
        self.display.setStyleSheet("font-size: 24px; padding: 5px; border: 2px solid #ccc; border-radius: 5px;")
        self.layout.addWidget(self.display)
        
        # Grille boutons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('C', 3, 2), ('+', 3, 3),
            ('=', 4, 0, 1, 4)
        ]
        
        for btn_text, *pos in buttons:
            btn = QPushButton(btn_text)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            
            if btn_text == 'C':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #ffcccc; color: #c0392b;")
                btn.clicked.connect(self.clear)
            elif btn_text == '=':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #2ecc71; color: white;")
                btn.clicked.connect(self.calculate)
            else:
                btn.clicked.connect(lambda checked, x=btn_text: self.append(x))
            
            if len(pos) == 4:
                grid_layout.addWidget(btn, *pos)
            else:
                grid_layout.addWidget(btn, *pos)
                
        self.layout.addLayout(grid_layout)
        self.setLayout(self.layout)
        
    def append(self, text):
        self.display.setText(self.display.text() + text)
        
    def clear(self):
        self.display.clear()
        
    def calculate(self):
        try:
            expression = self.display.text().replace('x', '*')
            result = eval(expression)
            self.display.setText(str(result))
        except Exception:
            self.display.setText("Erreur")


class MiniCalculatorDialog(QDialog):
    """Mini Calculatrice avec ajout direct au panier"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💰 Montant Libre")
        self.setFixedSize(280, 380)
        self.value = 0
        layout = QVBoxLayout()
        
        # Écran d'affichage
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(60)
        self.display.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold;
            padding: 10px; 
            border: 2px solid #27ae60; 
            border-radius: 8px;
            background-color: #e8f5e9;
        """)
        layout.addWidget(self.display)
        
        # Grille de boutons numériques
        grid = QGridLayout()
        grid.setSpacing(5)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('00', 3, 1), ('C', 3, 2),
        ]
        
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(55)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: bold;
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            if text == 'C':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #ffcccc; color: #c0392b;")
                btn.clicked.connect(self.clear_display)
            else:
                btn.clicked.connect(lambda checked, t=text: self.add_digit(t))
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        
        # Bouton Ajouter
        add_btn = QPushButton("✅ AJOUTER AU PANIER")
        add_btn.setMinimumHeight(60)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        add_btn.clicked.connect(self.accept)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)
    
    def add_digit(self, digit):
        current = self.display.text()
        if current == "0":
            self.display.setText(digit)
        else:
            self.display.setText(current + digit)
    
    def clear_display(self):
        self.display.setText("0")
    
    def get_value(self):
        try:
            return int(self.display.text())
        except:
            return 0
