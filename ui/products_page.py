# -*- coding: utf-8 -*-
"""
Interface de gestion des produits
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QMenu, QAbstractItemView, QCompleter)

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from modules.products.product_manager import product_manager
from modules.products.category_manager import category_manager
from modules.suppliers.supplier_manager import supplier_manager
from modules.reports.reorder_report import generate_reorder_report
from core.logger import logger
from core.i18n import i18n_manager
from core.data_signals import data_signals

class ProductFormDialog(QDialog):
    """Dialogue d'ajout/modification de produit"""
    
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        _ = i18n_manager.get
        self.setWindowTitle(_("product_dialog_new") if not product else _("product_dialog_edit"))
        self.setMinimumWidth(500)
        self.suppliers = supplier_manager.get_all_suppliers()
        self.categories = category_manager.get_all_categories()
        self.setup_ui()
        
    def setup_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        
        # Onglets pour organiser les informations
        tabs = QTabWidget()
        
        # Onglet Général
        general_tab = QWidget()
        form_layout = QFormLayout()
        
        self.barcode_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.name_ar_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setInsertPolicy(QComboBox.NoInsert)
        self.category_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        
        # Fill Categories
        self.category_combo.addItem("", None)
        is_arabic = i18n_manager.current_language == 'ar'
        for c in self.categories:
            # Display Arabic name if in Arabic mode and available, else French name
            display_name = c['name_ar'] if is_arabic and c.get('name_ar') else c['name']
            self.category_combo.addItem(display_name, c['id'])
            
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        self.supplier_combo.setInsertPolicy(QComboBox.NoInsert)
        self.supplier_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.supplier_combo.addItem("", None)
        for s in self.suppliers:
            self.supplier_combo.addItem(s['company_name'], s['id'])
            
        self.description_edit = QLineEdit()
        
        form_layout.addRow(_("label_barcode"), self.barcode_edit)
        form_layout.addRow(_("label_fullname"), self.name_edit)
        form_layout.addRow(_("label_name_ar"), self.name_ar_edit)
        form_layout.addRow(_("label_category"), self.category_combo)
        form_layout.addRow(_("label_supplier"), self.supplier_combo)
        form_layout.addRow(_("label_description"), self.description_edit)
        # form_layout.addRow("Catégorie:", self.category_combo)
        
        general_tab.setLayout(form_layout)
        tabs.addTab(general_tab, _("tab_general"))
        
        # Onglet Prix & Stock
        price_tab = QWidget()
        price_layout = QFormLayout()
        
        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0, 1000000)
        self.purchase_price_spin.setSuffix(" DA")
        self.purchase_price_spin.setDecimals(2)
        
        self.selling_price_spin = QDoubleSpinBox()
        self.selling_price_spin.setRange(0, 1000000)
        self.selling_price_spin.setSuffix(" DA")
        self.selling_price_spin.setDecimals(2)
        
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 100000)
        
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setRange(0, 1000)
        self.min_stock_spin.setValue(10)
        
        self.expiry_date_edit = QDateEdit()
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        self.enable_expiry = QCheckBox(_("checkbox_expiry_date"))
        self.enable_expiry.toggled.connect(self.expiry_date_edit.setEnabled)
        self.expiry_date_edit.setEnabled(False)
        
        price_layout.addRow(_("label_purchase_price"), self.purchase_price_spin)
        price_layout.addRow(_("label_selling_price"), self.selling_price_spin)
        price_layout.addRow(_("label_initial_stock"), self.stock_spin)
        price_layout.addRow(_("label_min_stock"), self.min_stock_spin)
        price_layout.addRow(self.enable_expiry, self.expiry_date_edit)
        
        price_tab.setLayout(price_layout)
        tabs.addTab(price_tab, _("tab_price_stock"))

        # Section Création Unitaire (Déplacé ici)
        price_layout.addRow(QLabel(""))
        price_layout.addRow(QLabel(f"<b>{_('section_auto_create')}</b>"))
        
        # Auto-create unit checkbox (only for NEW products)
        self.auto_create_unit_check = QCheckBox(_("checkbox_auto_create"))
        self.auto_create_unit_check.setToolTip(_("checkbox_auto_create"))
        self.auto_create_unit_check.toggled.connect(self._toggle_unit_fields)
        price_layout.addRow(self.auto_create_unit_check)
        
        # Unit price field
        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0, 100000)
        self.unit_price_spin.setSuffix(" DA")
        self.unit_price_spin.setDecimals(2)
        self.unit_price_spin.setEnabled(False)
        price_layout.addRow(_("label_unit_price"), self.unit_price_spin) # Changed label key if needed, or reuse generic
        
        # Packing Quantity
        self.packing_qty_spin = QSpinBox()
        self.packing_qty_spin.setRange(1, 1000)
        self.packing_qty_spin.setValue(20)
        price_layout.addRow(_("label_packing_qty"), self.packing_qty_spin)

        

        
        layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton(_("btn_save"))
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        
        cancel_btn = QPushButton(_("btn_cancel"))
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Remplir si modification
        if self.product:
            self.barcode_edit.setText(self.product.get('barcode', ''))
            self.name_edit.setText(self.product.get('name', ''))
            self.name_ar_edit.setText(self.product.get('name_ar', ''))
            self.description_edit.setText(self.product.get('description', ''))
            self.purchase_price_spin.setValue(self.product.get('purchase_price', 0))
            self.selling_price_spin.setValue(self.product.get('selling_price', 0))
            self.stock_spin.setValue(int(self.product.get('stock_quantity', 0)))
            self.min_stock_spin.setValue(self.product.get('min_stock_level', 10))
            
            # Select Supplier
            supplier_id = self.product.get('supplier_id')
            if supplier_id:
                index = self.supplier_combo.findData(supplier_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)

            # Select Category
            category_id = self.product.get('category_id')
            if category_id:
                index = self.category_combo.findData(category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            
            if self.product.get('expiry_date'):
                self.enable_expiry.setChecked(True)
                self.expiry_date_edit.setDate(QDate.fromString(self.product['expiry_date'], "yyyy-MM-dd"))
            
            
            # Load Packing Qty
            packing_qty = self.product.get('packing_quantity', 20)
            self.packing_qty_spin.setValue(packing_qty if packing_qty else 20)
            
            # Hide auto-create for existing products (edit mode)
            self.auto_create_unit_check.setVisible(False)
            self.unit_price_spin.setVisible(False)

    
    def _toggle_unit_fields(self, checked):
        """Toggle unit price field visibility"""
        self.unit_price_spin.setEnabled(checked)
                
    def save(self):
        _ = i18n_manager.get
        if not self.name_edit.text() or self.selling_price_spin.value() <= 0:
            QMessageBox.warning(self, _("title_error"), _("msg_name_price_required"))
            return

        data = {
            'barcode': self.barcode_edit.text(),
            'name': self.name_edit.text(),
            'name_ar': self.name_ar_edit.text(),
            'description': self.description_edit.text(),
            'purchase_price': self.purchase_price_spin.value(),
            'selling_price': self.selling_price_spin.value(),
            'stock_quantity': self.stock_spin.value(),
            'min_stock_level': self.min_stock_spin.value(),
            'expiry_date': self.expiry_date_edit.date().toString("yyyy-MM-dd") if self.enable_expiry.isChecked() else None,
            'supplier_id': self.supplier_combo.currentData(),
            'category_id': self.category_combo.currentData(),
            'is_tobacco': 0, # Removed feature
            'parent_product_id': None, # Removed manual linking
            'packing_quantity': self.packing_qty_spin.value()
        }

        
        if self.product:
            success, msg = product_manager.update_product(self.product['id'], **data)
        else:
            success, msg, pack_id = product_manager.create_product(**data)
            
            # Auto-create Unit product if checkbox is checked
            if success and self.auto_create_unit_check.isChecked() and self.unit_price_spin.value() > 0:
                unit_name = f"{self.name_edit.text()}{_('unit_suffix_fr')}"
                # Use the product's own barcode if it has one; only auto-generate if empty
                unit_barcode = self.barcode_edit.text() + "-U" if self.barcode_edit.text() and not product_manager.get_product_by_barcode(self.barcode_edit.text() + "-U") else None
                
                name_ar = self.name_ar_edit.text()
                unit_name_ar = f"{name_ar}{_('unit_suffix_ar')}" if name_ar else None

                unit_data = {
                    'barcode': unit_barcode,
                    'name': unit_name,
                    'name_ar': unit_name_ar,
                    'description': _("unit_of").format(self.name_edit.text()),
                    'purchase_price': self.purchase_price_spin.value() / self.packing_qty_spin.value(),  # Cost per unit
                    'selling_price': self.unit_price_spin.value(),
                    'stock_quantity': 0,  # Start with 0, will be filled when pack is opened
                    'min_stock_level': 0,
                    'supplier_id': self.supplier_combo.currentData(),
                    'category_id': self.category_combo.currentData(),
                    'is_tobacco': 0,
                    'parent_product_id': pack_id,  # Link to the pack we just created
                    'packing_quantity': self.packing_qty_spin.value()
                }
                
                unit_success, unit_msg, unit_id = product_manager.create_product(**unit_data)
                if unit_success:
                    msg = _("msg_pack_unit_created")
                else:
                    msg = f"Paquet créé, mais erreur Unité: {unit_msg}"
            
        if success:
            self.accept()
        else:
            _ = i18n_manager.get
            QMessageBox.critical(self, _("title_error"), msg)

class ProductsPage(QWidget):
    """Page de gestion des produits"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_products()
        
        i18n_manager.language_changed.connect(self.update_ui_text)
        
        # Connect to real-time signals
        data_signals.inventory_changed.connect(self.load_products)
        data_signals.product_changed.connect(self.load_products)
        data_signals.products_changed.connect(self.load_products)
        self.update_ui_text()
        
    def init_ui(self):
        _ = i18n_manager.get
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3b82f6, stop:1 #2563eb);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        self.header = QLabel(_("products_title"))
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        title_layout.addWidget(self.header)
        
        self.subtitle = QLabel(_("products_subtitle"))
        self.subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        title_layout.addWidget(self.subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Stat rapide dans le header
        self.count_label = QLabel(_("products_count").format(0))
        self.count_label.setStyleSheet("""
            background-color: rgba(255,255,255,0.2);
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.count_label)
        
        layout.addWidget(header_frame)
        
        # Barre d'outils - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        # Recherche - Plus grande
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("placeholder_search_product_page"))
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
                border-color: #3b82f6;
                background-color: #eff6ff;
            }
        """)
        self.search_input.textChanged.connect(self.load_products)
        toolbar.addWidget(self.search_input)
        
        # Filtres - Plus grand
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(50)
        self.filter_combo.setMinimumWidth(180)
        self.filter_combo.addItems([
            _("filter_all_products"),
            _("filter_low_stock"),
            _("filter_promo"),
            _("filter_expiring")
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
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        toolbar.addWidget(self.filter_combo)
        
        # Bouton Nouveau - Plus grand
        self.new_btn = QPushButton(_("btn_new_product"))
        self.new_btn.setMinimumHeight(50)
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        self.new_btn.clicked.connect(self.open_new_product_dialog)
        toolbar.addWidget(self.new_btn)
        
        # Bouton Importer - Plus grand
        self.import_btn = QPushButton(_("btn_import"))
        self.import_btn.setMinimumHeight(50)
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #7c3aed, stop:1 #6d28d9);
            }
        """)
        self.import_btn.clicked.connect(self.open_import_dialog)
        toolbar.addWidget(self.import_btn)

        # Bouton Commande Fournisseur - Nouveau
        self.order_btn = QPushButton(_("btn_order_report"))
        self.order_btn.setMinimumHeight(50)
        self.order_btn.setCursor(Qt.PointingHandCursor)
        self.order_btn.setToolTip(_("tooltip_order_report"))
        self.order_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #d97706, stop:1 #b45309);
            }
        """)
        self.order_btn.clicked.connect(self.generate_order_report)
        toolbar.addWidget(self.order_btn)
        
        layout.addLayout(toolbar)
        
        # Tableau - Style amélioré
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(_("table_headers_products_page"))
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: transparent;
                background-color: white;
                selection-background-color: #eff6ff;
                selection-color: #1e3a8a;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px 15px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
        """)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def update_ui_text(self):
        """Mettre à jour les textes de l'interface"""
        _ = i18n_manager.get
        is_rtl = i18n_manager.is_rtl()
        
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)
        
        self.header.setText(_("products_title"))
        self.subtitle.setText(_("products_subtitle"))
        self.search_input.setPlaceholderText(_("placeholder_search_product_page"))
        
        # Update filter combo items
        current_idx = self.filter_combo.currentIndex()
        self.filter_combo.setItemText(0, _("filter_all_products"))
        self.filter_combo.setItemText(1, _("filter_low_stock"))
        self.filter_combo.setItemText(2, _("filter_promo"))
        self.filter_combo.setItemText(3, _("filter_expiring"))
        self.filter_combo.setCurrentIndex(current_idx)
        
        self.new_btn.setText(_("btn_new_product"))
        self.import_btn.setText(_("btn_import"))
        self.order_btn.setText(_("btn_order_report"))
        self.order_btn.setToolTip(_("tooltip_order_report"))
        
        # Update table headers
        headers = _("table_headers_products_page")
        self.table.setHorizontalHeaderLabels(headers)
        
        # Update count label if visible
        if hasattr(self, 'count_label') and self.count_label:
            count = self.table.rowCount()
            self.count_label.setText(_("products_count").format(count))
        
    def load_products(self):
        _ = i18n_manager.get
        search = self.search_input.text()
        filter_idx = self.filter_combo.currentIndex()
        
        products = []
        if filter_idx == 1: # Low Stock
            products = product_manager.get_low_stock_products()
        elif filter_idx == 2: # Promo
            products = product_manager.get_promoted_products()
        elif filter_idx == 3: # Expiring
            products = product_manager.get_expiring_products()
        else:
            products = product_manager.search_products(search) if search else product_manager.get_all_products(limit=100)
            
        self.count_label.setText(_("products_count").format(len(products)))
            
        self.table.setRowCount(0)
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Stock alert color
            bg_color = None
            if p['stock_quantity'] <= p['min_stock_level']:
                bg_color = QColor("#ffebee") # Rouge clair
            
            # Items
            items = [
                p.get('barcode', ''),
                p['name'],
                f"{float(p['selling_price']):g} DA",
                str(p['stock_quantity']),
                p.get('expiry_date', '-'),
                f"{p.get('discount_percentage', 0):g}%" if p.get('is_on_promotion') else "-"
            ]
            
            for i, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                if bg_color:
                    item.setBackground(bg_color)
                self.table.setItem(row, i, item)
                
            # Boutons Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, x=p: self.open_edit_dialog(x))
            
            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=p['id']: self.delete_product(x))
            
            # Bouton imprimer code-barres
            print_btn = QPushButton("🏷️")
            print_btn.setFixedSize(30, 30)
            print_btn.setToolTip(_("tooltip_print_barcode"))
            print_btn.clicked.connect(lambda checked, x=p: self.print_barcode(x))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            action_layout.addWidget(print_btn)
            self.table.setCellWidget(row, 6, action_widget)
            
    def open_new_product_dialog(self):
        dialog = ProductFormDialog(parent=self)
        if dialog.exec_():
            self.load_products()
            
    def open_import_dialog(self):
        """Ouvrir le dialogue d'importation"""
        from ui.import_dialog import ImportDialog
        if ImportDialog(parent=self).exec_():
            self.load_products()
            
    def open_edit_dialog(self, product):
        dialog = ProductFormDialog(product, parent=self)
        if dialog.exec_():
            self.load_products()
            
    def delete_product(self, product_id):
        _ = i18n_manager.get
        confirm = QMessageBox.question(self, _("confirm_delete_customer_title"), _("msg_confirm_delete_product"), QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            product_manager.delete_product(product_id)
            self.load_products()

    def print_barcode(self, product):
        """Afficher et imprimer le code-barres d'un produit (16.83×22.86mm)"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
            from PyQt5.QtGui import QPainter, QFont, QImage, QPen
            from PyQt5.QtCore import Qt, QRectF, QSizeF
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            
            barcode_value = product.get('barcode', '')
            product_name = product.get('name', 'Produit')
            price = product.get('selling_price', 0)
            
            if not barcode_value:
                _ = i18n_manager.get
                QMessageBox.warning(self, _("title_error"), _("msg_no_barcode"))
                return
            
            # Label dimensions in mm
            LABEL_W_MM = 16.83
            LABEL_H_MM = 22.86
            
            # DPI for rendering preview (higher = sharper)
            PREVIEW_DPI = 300
            PREVIEW_SCALE = 4  # Scale up for display
            
            # Pixel dimensions for preview image
            px_w = int(LABEL_W_MM / 25.4 * PREVIEW_DPI)
            px_h = int(LABEL_H_MM / 25.4 * PREVIEW_DPI)
            
            def render_barcode_image():
                """Render barcode label to QImage"""
                img = QImage(px_w, px_h, QImage.Format_RGB32)
                img.fill(Qt.white)
                
                painter = QPainter(img)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.TextAntialiasing)
                
                # Scale factor (pixels per mm)
                ppmm = PREVIEW_DPI / 25.4
                
                # Draw product name at top (truncated)
                name_display = product_name[:15] + "..." if len(product_name) > 15 else product_name
                font_name = QFont("Arial", max(1, int(3.5 * ppmm / 4)), QFont.Bold)
                painter.setFont(font_name)
                name_rect = QRectF(0.5 * ppmm, 0.5 * ppmm, (LABEL_W_MM - 1) * ppmm, 4 * ppmm)
                painter.drawText(name_rect, Qt.AlignCenter | Qt.TextWordWrap, name_display)
                
                # Draw barcode using simple Code128-like bars representation
                # Generate Code128 barcode pattern
                bars = _generate_code128_bars(barcode_value)
                if bars:
                    bar_area_x = 1.0 * ppmm
                    bar_area_y = 5.0 * ppmm
                    bar_area_w = (LABEL_W_MM - 2.0) * ppmm
                    bar_area_h = 9 * ppmm
                    
                    total_bars = len(bars)
                    bar_width = bar_area_w / total_bars if total_bars > 0 else 1
                    
                    painter.setPen(Qt.NoPen)
                    for i, bar in enumerate(bars):
                        if bar == '1':
                            painter.setBrush(Qt.black)
                            painter.drawRect(QRectF(
                                bar_area_x + i * bar_width,
                                bar_area_y,
                                bar_width + 0.5,  # Slight overlap to avoid gaps
                                bar_area_h
                            ))
                
                # Draw barcode text below bars
                font_code = QFont("Consolas", max(1, int(2.5 * ppmm / 4)))
                painter.setFont(font_code)
                painter.setPen(Qt.black)
                code_rect = QRectF(0, 14.5 * ppmm, LABEL_W_MM * ppmm, 3 * ppmm)
                painter.drawText(code_rect, Qt.AlignCenter, barcode_value)
                
                # Draw price at bottom
                font_price = QFont("Arial", max(1, int(3.5 * ppmm / 4)), QFont.Bold)
                painter.setFont(font_price)
                price_rect = QRectF(0, 18 * ppmm, LABEL_W_MM * ppmm, 4 * ppmm)
                painter.drawText(price_rect, Qt.AlignCenter, f"{price:.0f} DA")
                
                painter.end()
                return img
            
            def _generate_code128_bars(data):
                """Generate a simple barcode bar pattern for display"""
                # Code 128B encoding
                CODE128_START_B = 104
                CODE128_STOP = 106
                
                # Patterns for Code 128 (each character = 6 bars + 6 spaces = string of 0s and 1s)
                PATTERNS = [
                    "11011001100", "11001101100", "11001100110", "10010011000", "10010001100",
                    "10001001100", "10011001000", "10011000100", "10001100100", "11001001000",
                    "11001000100", "11000100100", "10110011100", "10011011100", "10011001110",
                    "10111001100", "10011101100", "10011100110", "11001110010", "11001011100",
                    "11001001110", "11011100100", "11001110100", "11101101110", "11101001100",
                    "11100101100", "11100100110", "11101100100", "11100110100", "11100110010",
                    "11011011000", "11011000110", "11000110110", "10100011000", "10001011000",
                    "10001000110", "10110001000", "10001101000", "10001100010", "11010001000",
                    "11000101000", "11000100010", "10110111000", "10110001110", "10001101110",
                    "10111011000", "10111000110", "10001110110", "11101110110", "11010001110",
                    "11000101110", "11011101000", "11011100010", "11011101110", "11101011000",
                    "11101000110", "11100010110", "11101101000", "11101100010", "11100011010",
                    "11101111010", "11001000010", "11110001010", "10100110000", "10100001100",
                    "10010110000", "10010000110", "10000101100", "10000100110", "10110010000",
                    "10110000100", "10011010000", "10011000010", "10000110100", "10000110010",
                    "11000010010", "11001010000", "11110111010", "11000010100", "10001111010",
                    "10100111100", "10010111100", "10010011110", "10111100100", "10011110100",
                    "10011110010", "11110100100", "11110010100", "11110010010", "11011011110",
                    "11011110110", "11110110110", "10101111000", "10100011110", "10001011110",
                    "10111101000", "10111100010", "11110101000", "11110100010", "10111011110",
                    "10111101110", "11101011110", "11110101110", "11010000100", "11010010000",
                    "11010011100", "1100011101011",
                ]
                
                result = ""
                # Start code B
                result += PATTERNS[CODE128_START_B]
                
                checksum = CODE128_START_B
                for i, char in enumerate(data):
                    code = ord(char) - 32
                    if 0 <= code < len(PATTERNS):
                        result += PATTERNS[code]
                        checksum += code * (i + 1)
                
                # Checksum
                checksum_val = checksum % 103
                if checksum_val < len(PATTERNS):
                    result += PATTERNS[checksum_val]
                
                # Stop code
                result += PATTERNS[CODE128_STOP]
                
                return result
            
            # Render the barcode image
            barcode_img = render_barcode_image()
            
            # Create preview dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Code-barres: {product_name}")
            dialog.setMinimumSize(350, 400)
            
            dlg_layout = QVBoxLayout(dialog)
            
            # Preview label (scaled up for visibility)
            from PyQt5.QtGui import QPixmap
            preview_label = QLabel()
            pixmap = QPixmap.fromImage(barcode_img)
            scaled_pixmap = pixmap.scaled(
                px_w * PREVIEW_SCALE // PREVIEW_DPI * 96,
                px_h * PREVIEW_SCALE // PREVIEW_DPI * 96, 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            preview_label.setPixmap(scaled_pixmap)
            preview_label.setAlignment(Qt.AlignCenter)
            preview_label.setStyleSheet("border: 1px dashed #ccc; padding: 10px; background: white;")
            dlg_layout.addWidget(preview_label)
            
            # Info label
            info = QLabel(f"Taille: {LABEL_W_MM} × {LABEL_H_MM} mm")
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("color: #666; font-size: 12px;")
            dlg_layout.addWidget(info)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            print_btn = QPushButton("🖨️ Imprimer")
            print_btn.setMinimumHeight(40)
            print_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6; color: white;
                    border: none; border-radius: 8px;
                    font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background-color: #2563eb; }
            """)
            
            def do_print():
                printer = QPrinter(QPrinter.HighResolution)
                printer.setPageSizeMM(QSizeF(LABEL_W_MM, LABEL_H_MM))
                printer.setFullPage(True)
                
                print_dialog = QPrintDialog(printer, dialog)
                if print_dialog.exec_() == QDialog.Accepted:
                    p = QPainter(printer)
                    # Scale image to fill the printer page
                    page_rect = printer.pageRect()
                    p.drawImage(page_rect, barcode_img)
                    p.end()
                    logger.info(f"Code-barres imprimé: {barcode_value}")
            
            print_btn.clicked.connect(do_print)
            btn_layout.addWidget(print_btn)
            
            close_btn = QPushButton("Fermer")
            close_btn.setMinimumHeight(40)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e5e7eb; color: #374151;
                    border: none; border-radius: 8px;
                    font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background-color: #d1d5db; }
            """)
            close_btn.clicked.connect(dialog.close)
            btn_layout.addWidget(close_btn)
            
            dlg_layout.addLayout(btn_layout)
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Erreur code-barres: {e}")
            _ = i18n_manager.get
            QMessageBox.critical(self, _("title_error"), f"Erreur code-barres: {e}")

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Obtenir le produit sélectionné
        row = self.table.currentRow()
        if row < 0:
            return
            
        # TODO: ID is tricky to get from row if not stored. 
        # Better storing objects or ID in hidden column. 
        # For now, I rely on the search providing the same order but that's risky.
        # Let's fix this in load_products by storing ID in UserRole.
        pass # To be implemented if requested, simpler actions button covers it.

    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre à la page Produits"""
        if is_dark:
            # Mode sombre
            self.table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #555;
                    border-radius: 10px;
                    background-color: #34495e;
                    gridline-color: #555;
                    font-size: 14px;
                    color: white;
                }
                QTableWidget::item {
                    padding: 10px;
                    color: white;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    padding: 12px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #3d566e;
                }
            """)
            
            self.search_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #555;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 15px;
                    background-color: #34495e;
                    color: white;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            
            self.filter_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #555;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 14px;
                    background-color: #34495e;
                    color: white;
                }
            """)
        else:
            # Mode clair
            self.table.setStyleSheet("""
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
                    background-color: #3498db;
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
            """)
            
            self.search_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 15px;
                    background-color: white;
                    color: #333;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            
            self.filter_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 14px;
                    background-color: white;
                }
            """)

    def refresh(self):
        """Rafraîchir les données"""
        self.load_products()

    def generate_order_report(self):
        """Générer le rapport de commande"""
        success, msg = generate_reorder_report()
        if not success:
            QMessageBox.warning(self, "Attention", msg)

