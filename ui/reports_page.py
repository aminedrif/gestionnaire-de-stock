# -*- coding: utf-8 -*-
"""
Interface des rapports
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QHeaderView, QTabWidget, QGridLayout, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from modules.reports.profit_report import profit_report_manager
from core.logger import logger
import datetime

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
        self.refresh_data()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar (Période)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Période:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30)) # 30 derniers jours par défaut
        toolbar.addWidget(self.start_date)
        
        toolbar.addWidget(QLabel(" à "))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        toolbar.addWidget(self.end_date)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # KPI Cards (Cartes indicateurs)
        kpi_layout = QHBoxLayout()
        self.card_sales = KPICard("Chiffre d'Affaires", "0 DA", "#3498db")
        self.card_profit = KPICard("Bénéfice Net", "0 DA", "#2ecc71")
        self.card_margin = KPICard("Marge", "0%", "#f1c40f")
        self.card_count = KPICard("Nombre de Ventes", "0", "#9b59b6")
        
        kpi_layout.addWidget(self.card_sales)
        kpi_layout.addWidget(self.card_profit)
        kpi_layout.addWidget(self.card_margin)
        kpi_layout.addWidget(self.card_count)
        layout.addLayout(kpi_layout)
        
        # Onglets Détails
        tabs = QTabWidget()
        
        # Onglet 1: Ventes par jour
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(4)
        self.daily_table.setHorizontalHeaderLabels(["Date", "Ventes", "Coût", "Bénéfice"])
        self.daily_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.daily_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only
        tabs.addTab(self.daily_table, "Ventes par Jour")
        
        # Onglet 2: Top Produits (Rentabilité)
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["Produit", "Qté Vendue", "CA", "Bénéfice", "Marge"])
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.product_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only
        tabs.addTab(self.product_table, "Top Produits")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
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

    def refresh(self):
        """Rafraîchir les données"""
        self.refresh_data()
