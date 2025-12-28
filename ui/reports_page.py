# -*- coding: utf-8 -*-
"""
Interface des rapports
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QHeaderView, QTabWidget, QGridLayout, 
                             QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from modules.reports.profit_report import profit_report_manager
from core.logger import logger
import datetime

from core.i18n import i18n_manager

class KPICard(QFrame):
    def __init__(self, title, value, color="#3498db", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
                border-left: 5px solid {color};
            }}
        """)
        self.setMinimumSize(200, 100)
        
        layout = QVBoxLayout()
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")
        layout.addWidget(title_lbl)
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; border: none;")
        self.value_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.value_lbl)
        
        self.setLayout(layout)
        
    def set_value(self, value):
        self.value_lbl.setText(str(value))

class ReportsPage(QWidget):
    """Page des rapports et statistiques"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        # Connect to language change
        i18n_manager.language_changed.connect(self.update_ui_text)
        
        # Initial load
        self.refresh_data()
        
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
        # Save current dates
        current_start = self.start_date.date()
        current_end = self.end_date.date()
        
        # Remove old container
        if hasattr(self, 'container'):
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
        
        # Restore dates and Refresh Data
        self.start_date.setDate(current_start)
        self.end_date.setDate(current_end)
        self.refresh_data()

    def build_ui_content(self, parent_widget):
        _ = i18n_manager.get
        layout = QVBoxLayout(parent_widget)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel(_('reports_title'))
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Toolbar (Période)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        period_label = QLabel(_('label_period'))
        period_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        toolbar.addWidget(period_label)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setMinimumHeight(50)
        self.start_date.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
        """)
        toolbar.addWidget(self.start_date)
        
        toolbar.addWidget(QLabel(_('label_to')))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(50)
        self.end_date.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
        """)
        toolbar.addWidget(self.end_date)
        
        refresh_btn = QPushButton(_('btn_refresh_report'))
        refresh_btn.setMinimumHeight(50)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # KPI Cards (Cartes indicateurs)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        self.card_sales = KPICard(_('kpi_turnover'), "0 DA", "#3498db")
        self.card_profit = KPICard(_('kpi_net_profit'), "0 DA", "#2ecc71")
        self.card_margin = KPICard(_('kpi_margin'), "0%", "#f1c40f")
        self.card_count = KPICard(_('kpi_sale_count'), "0", "#9b59b6")
        
        kpi_layout.addWidget(self.card_sales)
        kpi_layout.addWidget(self.card_profit)
        kpi_layout.addWidget(self.card_margin)
        kpi_layout.addWidget(self.card_count)
        layout.addLayout(kpi_layout)
        
        # Style pour les tables
        table_style = """
            QTableWidget {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #f39c12;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """
        
        # Onglets Détails
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border: none; } QTabBar::tab { padding: 10px 20px; font-size: 14px; }")
        
        # Onglet 1: Ventes par jour
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(4)
        self.daily_table.setHorizontalHeaderLabels(_('table_headers_daily'))
        self.daily_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.daily_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.daily_table.setAlternatingRowColors(True)
        self.daily_table.verticalHeader().setDefaultSectionSize(45)
        self.daily_table.setStyleSheet(table_style)
        tabs.addTab(self.daily_table, _('tab_daily_sales'))
        
        # Onglet 2: Top Produits
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(_('table_headers_products_report'))
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.product_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.verticalHeader().setDefaultSectionSize(45)
        self.product_table.setStyleSheet(table_style)
        tabs.addTab(self.product_table, _('tab_top_products'))
        
        # Onglet 3: Ventes par Utilisateur
        self.user_sales_table = QTableWidget()
        self.user_sales_table.setColumnCount(5)
        self.user_sales_table.setHorizontalHeaderLabels(_('table_headers_users_report'))
        self.user_sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.user_sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_sales_table.setAlternatingRowColors(True)
        self.user_sales_table.verticalHeader().setDefaultSectionSize(45)
        self.user_sales_table.setStyleSheet(table_style)
        tabs.addTab(self.user_sales_table, _('tab_user_sales'))
        
        # Onglet 4: Clôture / Résumé Financier
        self.closure_widget = QWidget()
        closure_layout = QVBoxLayout(self.closure_widget)
        self.closure_label = QLabel(_('label_closure_info'))
        self.closure_label.setStyleSheet("font-size: 16px; line-height: 1.5; padding: 20px; background: white; border-radius: 10px;")
        self.closure_label.setAlignment(Qt.AlignTop)
        closure_layout.addWidget(self.closure_label)
        closure_layout.addStretch()
        
        print_closure_btn = QPushButton(_('btn_print_closure'))
        print_closure_btn.clicked.connect(self.print_closure_summary)
        closure_layout.addWidget(print_closure_btn)
        
        tabs.addTab(self.closure_widget, _('tab_closure'))
        
        layout.addWidget(tabs)

    def refresh_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        # 1. Global KPIs
        stats = profit_report_manager.get_profit_by_period(start, end)
        
        self.card_sales.set_value(f"{stats['total_revenue']:,.2f} DA")
        self.card_profit.set_value(f"{stats['net_profit']:,.2f} DA")
        self.card_margin.set_value(f"{stats['profit_margin']}%")
        self.card_count.set_value(str(stats['sale_count']))
        
        # 2. Daily Trend
        trend = profit_report_manager.get_daily_profit_trend(start, end)
        self.daily_table.setRowCount(0)
        for day in trend:
            row = self.daily_table.rowCount()
            self.daily_table.insertRow(row)
            self.daily_table.setItem(row, 0, QTableWidgetItem(day['date']))
            self.daily_table.setItem(row, 1, QTableWidgetItem(f"{day['revenue']:.2f}"))
            self.daily_table.setItem(row, 2, QTableWidgetItem(f"{day['cost']:.2f}"))
            
            profit_item = QTableWidgetItem(f"{day['profit']:.2f}")
            if day['profit'] > 0:
                profit_item.setForeground(QColor("green"))
            else:
                profit_item.setForeground(QColor("red"))
            self.daily_table.setItem(row, 3, profit_item)
            
        # 3. Top Products
        products = profit_report_manager.get_profit_by_product(start, end)
        self.product_table.setRowCount(0)
        for p in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            self.product_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(p['quantity_sold'])))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{p['revenue']:.2f}"))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{p['profit']:.2f}"))
            self.product_table.setItem(row, 4, QTableWidgetItem(f"{p['profit_margin']}%"))
        
        # 4. Sales by User
        self.load_sales_by_user(start, end)
        
        # 5. Financial Closure Summary
        self.update_closure_summary(start, end)

    def load_sales_by_user(self, start_date: str, end_date: str):
        """Charger les ventes par utilisateur"""
        from database.db_manager import db
        
        query = """
            SELECT 
                u.id,
                u.full_name,
                u.role,
                COUNT(s.id) as sale_count,
                COALESCE(SUM(s.total_amount), 0) as total_revenue,
                COALESCE(SUM(
                    (SELECT SUM((si.unit_price - si.purchase_price) * si.quantity)
                     FROM sale_items si
                     WHERE si.sale_id = s.id)
                ), 0) as total_profit
            FROM users u
            LEFT JOIN sales s ON u.id = s.cashier_id 
                AND s.status = 'completed'
                AND DATE(s.sale_date) BETWEEN ? AND ?
            WHERE u.is_active = 1
            GROUP BY u.id, u.full_name, u.role
            ORDER BY total_revenue DESC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        
        self.user_sales_table.setRowCount(0)
        for user in results:
            row = self.user_sales_table.rowCount()
            self.user_sales_table.insertRow(row)
            
            self.user_sales_table.setItem(row, 0, QTableWidgetItem(user['full_name']))
            self.user_sales_table.setItem(row, 1, QTableWidgetItem(user['role']))
            self.user_sales_table.setItem(row, 2, QTableWidgetItem(str(user['sale_count'])))
            
            revenue_item = QTableWidgetItem(f"{user['total_revenue']:.2f} DA")
            revenue_item.setForeground(QColor("#3498db"))
            self.user_sales_table.setItem(row, 3, revenue_item)
            
            profit_item = QTableWidgetItem(f"{user['total_profit']:.2f} DA")
            if user['total_profit'] > 0:
                profit_item.setForeground(QColor("green"))
            else:
                profit_item.setForeground(QColor("red"))
            self.user_sales_table.setItem(row, 4, profit_item)

    def update_closure_summary(self, start_date, end_date):
        _ = i18n_manager.get
        from database.db_manager import db
        
        query = """
            SELECT 
                payment_method,
                SUM(total_amount) as total,
                COUNT(id) as count
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ? AND status = 'completed'
            GROUP BY payment_method
        """
        results = db.execute_query(query, (start_date, end_date))
        
        # Group returns
        ret_res = db.fetch_one("SELECT SUM(return_amount) as total FROM returns", ()) # Placeholder, refine if date available
        
        # Calculate totals
        cash_total = 0
        credit_total = 0
        other_total = 0
        counts = {'cash':0, 'credit':0}
        
        for res in results:
            pm = res['payment_method']
            if pm == 'cash':
                cash_total = res['total']
                counts['cash'] = res['count']
            elif pm == 'credit':
                credit_total = res['total']
                counts['credit'] = res['count']
            else:
                other_total += res['total']
                
        summary_text = f"""
        <h2 style='color: #2c3e50;'>{_('closure_summary_title').format(start_date, end_date)}</h2>
        <hr>
        <table width='100%' style='font-size: 16px; border-collapse: collapse;'>
            <tr><td style='padding: 8px;'><b>{_('closure_cash')}</b></td><td align='right'>{cash_total:,.2f} DA ({counts['cash']})</td></tr>
            <tr><td style='padding: 8px;'><b>{_('closure_credit')}</b></td><td align='right'>{credit_total:,.2f} DA ({counts['credit']})</td></tr>
            <tr><td style='padding: 8px;'><b>{_('closure_other')}</b></td><td align='right'>{other_total:,.2f} DA</td></tr>
            <tr style='background-color: #f8f9fa;'><td style='padding: 8px;'><b>{_('closure_total')}</b></td><td align='right'><b>{(cash_total+credit_total+other_total):,.2f} DA</b></td></tr>
            <tr><td colspan='2'><br></td></tr>
            <tr><td style='padding: 8px; color: #e74c3c;'><b>{_('closure_returns')}</b></td><td align='right' style='color: #e74c3c;'>{ret_res['total'] or 0:,.2f} DA</td></tr>
        </table>
        """
        self.closure_label.setText(summary_text)

    def print_closure_summary(self):
        # Pourrait générer un PDF, mais pour l'instant on affiche un message
        QMessageBox.information(self, "Impression", "Le rapport de clôture a été généré (Simulé).")

    def refresh(self):
        """Rafraîchir les données"""
        self.refresh_data()

