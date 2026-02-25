# -*- coding: utf-8 -*-
"""
Page de gestion des catégories
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QMessageBox, QAbstractItemView,
                             QMenu, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from modules.products.category_manager import category_manager
from core.i18n import i18n_manager
from core.auth import auth_manager
from core.data_signals import data_signals

class CategoryDialog(QDialog):
    """Dialogue d'ajout/modification de catégorie"""
    
    def __init__(self, category=None, parent=None):
        super().__init__(parent)
        self.category = category
        self.category_manager = category_manager
        
        _ = i18n_manager.get
        self.setWindowTitle(_("category_dialog_new") if not category else _("category_dialog_edit"))
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        
        # Form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_ar_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        form_layout.addRow(_("label_name"), self.name_edit)
        form_layout.addRow(_("label_name_ar"), self.name_ar_edit)
        form_layout.addRow(_("label_description"), self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(_("btn_save"))
        save_btn.clicked.connect(self.save)
        # Using same green button style as other pages
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        cancel_btn = QPushButton(_("btn_cancel"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; 
                color: white; 
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Fill data if editing
        if self.category:
            self.name_edit.setText(self.category.get('name', ''))
            self.name_ar_edit.setText(self.category.get('name_ar', ''))
            self.description_edit.setText(self.category.get('description', ''))

    def save(self):
        _ = i18n_manager.get
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, _("title_error"), _("msg_name_required"))
            return

        data = {
            'name': name,
            'name_ar': self.name_ar_edit.text().strip(),
            'description': self.description_edit.text().strip()
        }
        
        if self.category:
            success, msg = self.category_manager.update_category(self.category['id'], **data)
        else:
            success, msg, _ = self.category_manager.create_category(**data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, _("title_error"), msg)

class CategoriesPage(QWidget):
    """Page de gestion des catégories"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_categories()
        
        # Connect to language change
        i18n_manager.language_changed.connect(self.update_ui_text)
        
        # Connect to data changes
        data_signals.categories_changed.connect(self.load_categories)

    def init_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête avec gradient (Similaire à CustomersPage)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        self.header = QLabel(_("setup_categories_title"))
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        title_layout.addWidget(self.header)
        
        self.subtitle = QLabel(_("setup_categories_subtitle") if _("setup_categories_subtitle") != "setup_categories_subtitle" else "Manage your product categories")
        self.subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        title_layout.addWidget(self.subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_category") if _("placeholder_search_category") != "placeholder_search_category" else "Search categories...")
        self.search_input.setMinimumHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ebf8ff;
            }
        """)
        self.search_input.textChanged.connect(self.load_categories)
        toolbar.addWidget(self.search_input)
        
        toolbar.addStretch()
        
        self.add_btn = QPushButton(_("btn_add_category"))
        self.add_btn.setMinimumHeight(45)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #2980b9, stop:1 #2475a8);
            }
        """)
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        # Check permissions
        if not auth_manager.has_permission('manage_products'):
            self.add_btn.hide()
            
        toolbar.addWidget(self.add_btn)
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            _("col_id"), _("col_name"), _("col_name_ar"), _("col_actions")
        ])
        
        # Style table (Matched to CustomersPage)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents) # Actions column
        
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: transparent;
                background-color: white;
                selection-background-color: #ebf8ff;
                selection-color: #1d4f91;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f0f9ff;
                padding: 10px 15px;
                border: none;
                border-bottom: 2px solid #bae6fd;
                font-weight: bold;
                color: #0369a1;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px 10px;
                border-bottom: 1px solid #f0f9ff;
            }
            QTableWidget::item:selected {
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f0f9ff;
            }
        """)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_categories(self):
        _ = i18n_manager.get
        categories = category_manager.get_all_categories()
        
        # Filter if search text
        search_text = self.search_input.text().lower()
        if search_text:
            categories = [c for c in categories if 
                          search_text in c['name'].lower() or 
                          (c.get('name_ar') and search_text in c['name_ar'].lower())]
        
        self.table.setRowCount(0)
        
        for c in categories:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(c['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(c['name']))
            
            # Name AR + Description combined or just Name AR? Table has 4 columns.
            # Header ID, Name, Name AR, Actions
            # Let's put description as tooltip or helper
            name_ar_item = QTableWidgetItem(c.get('name_ar', ''))
            name_ar_item.setToolTip(c.get('description', ''))
            self.table.setItem(row, 2, name_ar_item)
            
            # Actions
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(5, 2, 5, 2)
            hbox.setSpacing(5)
            
            if auth_manager.has_permission('manage_products'):
                edit_btn = QPushButton(_("btn_edit"))
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #f39c12;
                        border: 1px solid #f39c12;
                        border-radius: 4px;
                        padding: 4px 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f39c12;
                        color: white;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, x=c: self.open_edit_dialog(x))
                hbox.addWidget(edit_btn)
                
                del_btn = QPushButton(_("btn_delete"))
                del_btn.setCursor(Qt.PointingHandCursor)
                del_btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #e74c3c;
                        border: 1px solid #e74c3c;
                        border-radius: 4px;
                        padding: 4px 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e74c3c;
                        color: white;
                    }
                """)
                del_btn.clicked.connect(lambda checked, x=c['id']: self.delete_category(x))
                hbox.addWidget(del_btn)
            
            hbox.addStretch()
            self.table.setCellWidget(row, 3, widget)

    def open_add_dialog(self):
        dialog = CategoryDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_categories()

    def open_edit_dialog(self, category):
        dialog = CategoryDialog(category, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_categories()

    def delete_category(self, category_id):
        _ = i18n_manager.get
        if QMessageBox.question(self, _("confirm_delete_title"), _("confirm_delete_msg"), 
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            success, msg = category_manager.delete_category(category_id)
            if success:
                self.load_categories()
            else:
                QMessageBox.critical(self, _("title_error"), msg)

    def update_ui_text(self):
        _ = i18n_manager.get
        self.header.setText(_("setup_categories_title"))
        self.subtitle.setText(_("setup_categories_subtitle"))
        self.search_input.setPlaceholderText(_("placeholder_search_category"))
        self.add_btn.setText(_("btn_add_category"))
        
        self.table.setHorizontalHeaderLabels([
            _("col_id"), _("col_name"), _("col_name_ar"), _("col_actions")
        ])
        
        # We need to reload the table to update button texts
        self.load_categories()
