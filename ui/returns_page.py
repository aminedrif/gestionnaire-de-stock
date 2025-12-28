# -*- coding: utf-8 -*-
"""
Interface de gestion des retours et remboursements
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QFrame, QMessageBox, QHeaderView, QDoubleSpinBox, QSpinBox,
                             QAbstractItemView, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont, QIcon
from modules.sales.pos import pos_manager
from modules.sales.printer import printer_manager
from core.auth import auth_manager
from core.logger import logger
from core.i18n import i18n_manager
from database.db_manager import db

class ReturnsPage(QWidget):
    """Page de gestion des retours"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_sale = None
        self.return_items = {}  # {product_id: quantity_to_return}
        self.init_ui()
        # Connect to language change
        i18n_manager.language_changed.connect(self.update_ui_text)

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
        # Save state if needed (optional, here we might reset search but that's acceptable)
        
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
        
        # Restore state if current sale exists
        if self.current_sale:
            # We might want to re-display the current sale info if possible
            # For now, let's just clear it to avoid complexity, or we could call search again if we had the ID
            pass

    def build_ui_content(self, parent_widget):
        _ = i18n_manager.get
        layout = QVBoxLayout(parent_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)

        # En-tête
        header_layout = QHBoxLayout()
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0,0,0,0)
        
        title = QLabel(_('returns_title'))
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1f2937;")
        
        subtitle = QLabel(_('returns_subtitle'))
        subtitle.setStyleSheet("font-size: 14px; color: #6b7280;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Zone de recherche
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(20, 20, 20, 20)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_('placeholder_search_return'))
        self.search_input.setMinimumWidth(300)
        self.search_input.setFixedHeight(45)
        self.search_input.returnPressed.connect(self.search_sale)
        
        search_btn = QPushButton(_('btn_search_return'))
        search_btn.setIcon(QIcon("icons/search.png"))
        search_btn.setFixedSize(120, 45)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        search_btn.clicked.connect(self.search_sale)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        
        layout.addWidget(search_frame)

        # Info vente et Actions
        self.info_frame = QFrame()
        self.info_frame.setVisible(False)
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #eff6ff;
                border-radius: 12px;
                border: 1px solid #bfdbfe;
            }
        """)
        info_layout = QHBoxLayout(self.info_frame)
        
        self.sale_info_label = QLabel()
        self.sale_info_label.setStyleSheet("font-size: 16px; color: #1e40af; font-weight: bold;")
        
        self.btn_reprint = QPushButton(_('btn_reprint_ticket_return'))
        self.btn_reprint.setStyleSheet("background-color: #64748b; color: white; padding: 8px 15px; border-radius: 6px;")
        self.btn_reprint.clicked.connect(self.reprint_ticket)
        
        self.btn_cancel_all = QPushButton(_('btn_cancel_sale_return'))
        self.btn_cancel_all.setStyleSheet("background-color: #ef4444; color: white; padding: 8px 15px; border-radius: 6px; font-weight: bold;")
        self.btn_cancel_all.clicked.connect(self.cancel_entire_sale)

        info_layout.addWidget(self.sale_info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.btn_reprint)
        info_layout.addWidget(self.btn_cancel_all)
        
        layout.addWidget(self.info_frame)

        # Tableau des produits
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(_('table_headers_returns'))
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                gridline-color: #f3f4f6;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #374151;
            }
            QTableWidget::item {
                padding: 12px;
            }
        """)
        layout.addWidget(self.items_table)

        # Bouton Action Globale
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.btn_process_return = QPushButton(_('btn_process_return'))
        self.btn_process_return.setEnabled(False)
        self.btn_process_return.setFixedSize(250, 50)
        self.btn_process_return.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
            }
            QPushButton:hover:!disabled {
                background-color: #d97706;
            }
        """)
        self.btn_process_return.clicked.connect(self.process_partial_return)
        
        action_layout.addWidget(self.btn_process_return)
        layout.addLayout(action_layout)

    def search_sale(self):
        query = self.search_input.text().strip()
        if not query:
            return
            
        try:
            # Chercher par numéro de ticket ou ID
            if query.upper().startswith('VNT-'):
                sql = "SELECT * FROM sales WHERE sale_number = ?"
                param = (query.upper(),)
            else:
                sql = "SELECT * FROM sales WHERE id = ?"
                param = (query,)
                
            sale = db.fetch_one(sql, param)
            
            if not sale:
                self.search_input.setStyleSheet("border: 2px solid #ef4444;")
                self.info_frame.setVisible(False)
                self.items_table.setRowCount(0)
                self.btn_reprint.setEnabled(False)
                self.btn_cancel_all.setEnabled(False)
                self.btn_process_return.setEnabled(False)
                return
                
            self.search_input.setStyleSheet("")
            self.load_sale_details(sale)
            
        except Exception as e:
            logger.error(f"Erreur recherche vente: {e}")
            self.search_input.setStyleSheet("border: 2px solid #ef4444;")
            QMessageBox.critical(self, i18n_manager.get('title_error'), f"{i18n_manager.get('title_error')}: {e}")

    def load_sale_details(self, sale):
        _ = i18n_manager.get
        self.current_sale = sale
        self.return_items = {}
        
        # Afficher section info
        self.info_frame.setVisible(True)
        self.sale_info_label.setText(
            _('label_sale_info').format(sale['sale_number'], sale['total_amount'], sale['sale_date'])
        )
        
        # Enable/disable buttons based on sale status
        is_completed = sale['status'] == 'completed'
        self.btn_reprint.setEnabled(True) # Always allow reprinting if sale found
        self.btn_cancel_all.setEnabled(is_completed)
        self.btn_process_return.setEnabled(is_completed) # Will be further controlled by update_process_button

        # Charger items
        items = db.execute_query("""
            SELECT si.*, p.name as product_name 
            FROM sale_items si 
            JOIN products p ON si.product_id = p.id 
            WHERE si.sale_id = ?
        """, (sale['id'],))
        
        self.items_table.setRowCount(0)
        for row, item in enumerate(items):
            self.items_table.insertRow(row)
            
            # Produit
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            
            # Qté Achetée
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            
            # Prix Unit.
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            
            # Qté Retour (Editable)
            qty_spin = QSpinBox()
            qty_spin.setRange(0, item['quantity'])
            qty_spin.setValue(0)
            qty_spin.valueChanged.connect(lambda v, r=row, pid=item['product_id']: self.update_return_qty(r, pid, v))
            self.items_table.setCellWidget(row, 3, qty_spin)
            
            # Checkbox Selection
            chk_container = QWidget()
            chk_layout = QHBoxLayout(chk_container)
            chk_layout.setContentsMargins(0,0,0,0)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk = QCheckBox()
            # Connexion correcte: on passe la ligne pour récupérer le spinbox associé
            chk.stateChanged.connect(lambda state, r=row, pid=item['product_id']: self.toggle_selection(state, r, pid))
            chk_layout.addWidget(chk)
            self.items_table.setCellWidget(row, 4, chk_container)
        
        self.update_process_button() # Initial state for the button

    def update_return_qty(self, row, product_id, value):
        # Trouver la checkbox à cette ligne pour savoir si on doit l'activer
        widget = self.items_table.cellWidget(row, 4)
        if widget:
            chk = widget.findChild(QCheckBox)
            if chk:
                if value > 0:
                    chk.setChecked(True)
                    self.return_items[product_id] = value
                else:
                    # If quantity becomes 0, uncheck the box and remove from return_items
                    chk.setChecked(False)
                    if product_id in self.return_items:
                        del self.return_items[product_id]
        
        self.update_process_button()

    def toggle_selection(self, state, row, product_id):
        # Récupérer la valeur du spinbox à cette ligne
        spin_widget = self.items_table.cellWidget(row, 3)
        
        if state == Qt.Checked:
            qty = spin_widget.value()
            if qty == 0: # If checkbox is checked but spinbox is 0, set spinbox to 1
                spin_widget.setValue(1)
                self.return_items[product_id] = 1
            else:
                self.return_items[product_id] = qty
        else:
            # If checkbox is unchecked, set spinbox to 0 and remove from return_items
            spin_widget.setValue(0)
            if product_id in self.return_items:
                del self.return_items[product_id]
                
        self.update_process_button()

    def update_process_button(self):
        # Enable if at least one item selected with qty > 0 AND sale is completed
        if self.current_sale and self.current_sale['status'] == 'completed':
            has_items = len(self.return_items) > 0
            self.btn_process_return.setEnabled(has_items)
        else:
            self.btn_process_return.setEnabled(False)

    def process_partial_return(self):
        _ = i18n_manager.get
        if not self.return_items:
            QMessageBox.warning(self, _('title_warning'), _('msg_select_items_return'))
            return
            
        reply = QMessageBox.question(self, _('title_confirm'), 
                                   _('msg_confirm_partial_return'),
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            # Use pos_manager for return processing
            user = auth_manager.get_current_user()
            user_id = user['id'] if user else 1 # Default to 1 if no user logged in
            
            # Convert return_items dict to list of {'product_id': id, 'quantity': qty}
            items_for_manager = [{'product_id': pid, 'quantity': qty} for pid, qty in self.return_items.items()]

            success, msg, _ = pos_manager.process_return(
                self.current_sale['id'], items_for_manager, user_id, "Retour partiel client"
            )
            
            if success:
                QMessageBox.information(self, _('title_success'), msg)
                self.search_sale() # Rafraîchir
            else:
                QMessageBox.critical(self, _('title_error'), msg)

        except Exception as e:
            logger.error(f"Erreur retour: {e}")
            QMessageBox.critical(self, _('title_error'), f"{e}")

    def cancel_entire_sale(self):
        _ = i18n_manager.get
        if not self.current_sale:
            return

        reply = QMessageBox.question(self, _('title_confirm'), 
                                   _('confirm_cancel_sale_msg'),
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            success, msg = pos_manager.cancel_sale(self.current_sale['id'], "Annulation complète")
            
            if success:
                QMessageBox.information(self, _('title_success'), msg)
                self.search_sale() # Rafraîchir pour voir le nouveau statut
            else:
                QMessageBox.critical(self, _('title_error'), msg)
                
        except Exception as e:
            logger.error(f"Erreur annulation vente: {e}")
            QMessageBox.critical(self, _('title_error'), f"{e}")

    def reprint_ticket(self):
        if self.current_sale:
            printer_manager.print_receipt(self.current_sale)
            
    def refresh(self):
        """Méthode appelée lors du switch vers cette page"""
        self.search_input.setFocus()
        if self.current_sale:
            self.search_sale() # Actualiser les données de la vente affichée
