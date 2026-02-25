# -*- coding: utf-8 -*-
"""
Interface de l'historique des ventes
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QFrame, QMessageBox, QHeaderView, QAbstractItemView,
                             QDateEdit, QComboBox, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from modules.sales.pos import pos_manager
from modules.sales.printer import printer_manager
from core.auth import auth_manager
from core.logger import logger
from core.i18n import i18n_manager
from core.data_signals import data_signals
from core.logger import logger
from database.db_manager import db
from PyQt5.QtCore import pyqtSignal

class SaleDetailsDialog(QDialog):
    """Dialogue pour afficher les détails d'une vente"""
    def __init__(self, sale_id, parent=None):
        super().__init__(parent)
        self.sale_id = sale_id
        _ = i18n_manager.get
        self.setWindowTitle(_("sale_details_title").format(sale_id))
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft if i18n_manager.is_rtl() else Qt.LeftToRight)
        self.setup_ui()
        self.load_details()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout(self)
        
        # Info client/vendeur
        self.info_label = QLabel(_("label_loading"))
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.info_label)
        
        # Table des articles
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(_("table_headers_sale_items"))
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.items_table)
        
        # Total
        self.total_label = QLabel(_("label_dialog_total").format(0.0))
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(self.total_label)
        
        # Bouton fermer
        close_btn = QPushButton(_("btn_close_dialog"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
    def load_details(self):
        _ = i18n_manager.get
        sale = pos_manager.get_sale(self.sale_id)
        if not sale:
            self.info_label.setText(_("msg_sale_not_found_dialog"))
            return
            
        customer = sale.get('customer_name') or _("client_anonymous")
        cashier = sale.get('cashier_name') or _("unknown")
        date = sale.get('sale_date', '')
        
        self.info_label.setText(_("label_sale_info_detailed").format(date, customer, cashier, sale['status']))
        
        items = sale.get('items', [])
        self.items_table.setRowCount(0)
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['subtotal']:.2f}"))
            
        self.total_label.setText(_("label_dialog_total").format(sale['total_amount']))

class SalesHistoryPage(QWidget):
    """Page d'historique des ventes"""
    navigate_to = pyqtSignal(str, dict) # Pour navigation
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_sales()
        
        i18n_manager.language_changed.connect(self.update_ui_text)
        data_signals.sales_changed.connect(self.load_sales)
        self.update_ui_text()
        
    def init_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête Moderne
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4f46e5, stop:1 #7c3aed);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        self.header = QLabel(_("sales_history_title"))
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        title_layout.addWidget(self.header)
        
        self.subtitle = QLabel(_("sales_history_subtitle"))
        self.subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        title_layout.addWidget(self.subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Bouton export (Prévu)
        self.export_btn = QPushButton(_("btn_export_excel"))
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid white;
                border-radius: 8px;
                padding: 0 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.3); }
        """)
        self.export_btn.clicked.connect(self.export_to_csv)
        header_layout.addWidget(self.export_btn)
        
        layout.addWidget(header_frame)
        
        # Barre de Filtres
        filter_card = QFrame()
        filter_card.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e5e7eb;")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_sales"))
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.load_sales)
        filter_layout.addWidget(self.search_input)
        
        self.label_date_from = QLabel(_("label_date_from"))
        filter_layout.addWidget(self.label_date_from)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.dateChanged.connect(self.load_sales)
        filter_layout.addWidget(self.start_date)
        
        self.label_date_to = QLabel(_("label_date_to"))
        filter_layout.addWidget(self.label_date_to)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.load_sales)
        filter_layout.addWidget(self.end_date)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            _("filter_status_all"), 
            _("filter_status_completed"), 
            _("filter_status_cancelled"), 
            _("filter_status_returned")
        ])
        self.status_combo.currentIndexChanged.connect(self.load_sales)
        filter_layout.addWidget(self.status_combo)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(40)
        refresh_btn.clicked.connect(self.load_sales)
        filter_layout.addWidget(refresh_btn)
        
        layout.addWidget(filter_card)
        
        # Tableau
        self.sales_table = QTableWidget()
        cols = _("table_headers_sales")
        # Ensure we only use 7 columns if we don't have permission for profit
        if not auth_manager.has_permission('view_reports'):
             cols = cols[:-1] # Remove Profit column
            
        self.sales_table.setColumnCount(len(cols))
        self.sales_table.setHorizontalHeaderLabels(cols)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sales_table.doubleClicked.connect(self.view_sale_details)
        layout.addWidget(self.sales_table)
        
        # Boutons d'actions en bas
        actions_layout = QHBoxLayout()
        
        self.details_btn = QPushButton(_("btn_view_details"))
        self.details_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.details_btn.clicked.connect(self.view_sale_details)
        actions_layout.addWidget(self.details_btn)
        
        self.reprint_btn = QPushButton(_("btn_reprint"))
        self.reprint_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.reprint_btn.clicked.connect(self.reprint_sale)
        self.reprint_btn.clicked.connect(self.reprint_sale)
        actions_layout.addWidget(self.reprint_btn)
        
        self.return_btn = QPushButton(_("btn_return_action"))
        self.return_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        self.return_btn.clicked.connect(self.open_return)
        actions_layout.addWidget(self.return_btn)
        
        actions_layout.addStretch()
        
        # Résumé Rapide
        self.summary_label = QLabel(_("label_loading"))
        self.summary_label.setStyleSheet("font-weight: bold; color: #4b5563; font-size: 14px;")
        actions_layout.addWidget(self.summary_label)
        
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
        
    def update_ui_text(self):
        """Mettre à jour les textes de l'interface"""
        _ = i18n_manager.get
        is_rtl = i18n_manager.is_rtl()
        
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)
        
        self.header.setText(_("sales_history_title"))
        self.subtitle.setText(_("sales_history_subtitle"))
        self.export_btn.setText(_("btn_export_excel"))
        self.search_input.setPlaceholderText(_("placeholder_search_sales"))
        
        self.label_date_from.setText(_("label_date_from"))
        self.label_date_to.setText(_("label_date_to"))
        
        # Update Combo
        self.status_combo.setItemText(0, _("filter_status_all"))
        self.status_combo.setItemText(1, _("filter_status_completed"))
        self.status_combo.setItemText(2, _("filter_status_cancelled"))
        self.status_combo.setItemText(3, _("filter_status_returned"))
        
        self.details_btn.setText(_("btn_view_details"))
        self.reprint_btn.setText(_("btn_reprint"))
        self.return_btn.setText(_("btn_return_action"))
        
        # Headers
        cols = _("table_headers_sales")
        if not auth_manager.has_permission('view_reports'):
             cols = cols[:-1]
        self.sales_table.setHorizontalHeaderLabels(cols)
        
    def load_sales(self):
        search = self.search_input.text().strip()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        status_idx = self.status_combo.currentIndex()
        
        query = """
            SELECT s.*, u.full_name as cashier_name, c.full_name as customer_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
        """
        params = [start, end]
        
        if search:
            query += " AND (s.sale_number LIKE ? OR c.full_name LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
            
        if status_idx > 0:
            status_map = {1: 'completed', 2: 'cancelled', 3: 'returned'}
            query += " AND s.status = ?"
            params.append(status_map[status_idx])
            
        query += " ORDER BY s.sale_date DESC"
        
        results = db.execute_query(query, tuple(params))
        self.sales_table.setRowCount(0)
        
        total_ca = 0
        total_profit = 0
        
        for sale in results:
            row = self.sales_table.rowCount()
            self.sales_table.insertRow(row)
            
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale['id'])))
            self.sales_table.setItem(row, 1, QTableWidgetItem(sale['sale_number']))
            self.sales_table.setItem(row, 2, QTableWidgetItem(sale['sale_date']))
            self.sales_table.setItem(row, 3, QTableWidgetItem(sale['customer_name'] or "Public"))
            self.sales_table.setItem(row, 4, QTableWidgetItem(sale['cashier_name'] or "Système"))
            self.sales_table.setItem(row, 5, QTableWidgetItem(f"{sale['total_amount']:.2f}"))
            
            status_item = QTableWidgetItem(sale['status'])
            if sale['status'] == 'completed':
                status_item.setForeground(QColor("#059669"))
            elif sale['status'] == 'cancelled':
                status_item.setForeground(QColor("#dc2626"))
            else:
                status_item.setForeground(QColor("#d97706"))
            self.sales_table.setItem(row, 6, QTableWidgetItem(status_item))
            
            total_ca += sale['total_amount'] if sale['status'] == 'completed' else 0
            
            # Calculer bénéfice si autorisé
            if auth_manager.has_permission('view_reports'):
                # On pourrait faire un JOIN pour optimiser mais on va faire simple pour l'instant
                profit_query = "SELECT SUM((unit_price - purchase_price) * quantity) as profit FROM sale_items WHERE sale_id = ?"
                p_res = db.fetch_one(profit_query, (sale['id'],))
                profit = p_res['profit'] or 0 if sale['status'] == 'completed' else 0
                total_profit += profit
                self.sales_table.setItem(row, 7, QTableWidgetItem(f"{profit:.2f}"))
                
        _ = i18n_manager.get
        self.summary_label.setText(f"{_('summary_total_ca').format(total_ca)} | {_('summary_total_profit').format(total_profit)}")

    def view_sale_details(self):
        row = self.sales_table.currentRow()
        if row < 0: return
        sale_id = int(self.sales_table.item(row, 0).text())
        dialog = SaleDetailsDialog(sale_id, self)
        dialog.exec_()
        
        dialog = SaleDetailsDialog(sale_id, self)
        dialog.exec_()

    def open_return(self):
        """Ouvrir la page de retour pour cette vente"""
        row = self.sales_table.currentRow()
        if row < 0: return
        
        sale_id = int(self.sales_table.item(row, 0).text())
        # Naviguer vers la page retours
        self.navigate_to.emit("returns", {"load_sale": sale_id})
        
    def reprint_sale(self):
        row = self.sales_table.currentRow()
        if row < 0: return
        sale_id = int(self.sales_table.item(row, 0).text())
        sale = pos_manager.get_sale(sale_id)
        if sale:
            try:
                _ = i18n_manager.get
                printer_manager.print_receipt(sale)
                QMessageBox.information(self, "Impression", _("msg_print_sent"))
            except Exception as e:
                QMessageBox.critical(self, _("title_error"), f"Erreur d'impression: {e}")

    def export_to_csv(self):
        import csv
        import os
        from PyQt5.QtWidgets import QFileDialog
        
        path, _ = QFileDialog.getSaveFileName(self, "Exporter Historique", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                # Header
                headers = []
                for i in range(self.sales_table.columnCount()):
                    headers.append(self.sales_table.horizontalHeaderItem(i).text())
                writer.writerow(headers)
                
                # Rows
                for r in range(self.sales_table.rowCount()):
                    row_data = []
                    for c in range(self.sales_table.columnCount()):
                        item = self.sales_table.item(r, c)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                    
            _ = i18n_manager.get
            QMessageBox.information(self, _("title_success"), _("msg_export_success").format(path))
        except Exception as e:
            QMessageBox.critical(self, _("title_error"), f"Erreur lors de l'export: {e}")

    def filter_by_customer(self, customer_name):
        """Set search term to customer name and reload"""
        self.search_input.setText(customer_name)
        # load_sales is already connected to textChanged
        
    def refresh(self):
        self.load_sales()
