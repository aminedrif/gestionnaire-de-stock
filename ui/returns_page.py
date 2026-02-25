from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QFrame, QMessageBox, QHeaderView, QDoubleSpinBox, QSpinBox,
                             QAbstractItemView, QCheckBox, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont, QIcon
from modules.sales.pos import pos_manager
from modules.sales.printer import printer_manager
from core.auth import auth_manager
from core.logger import logger
from core.i18n import i18n_manager
from database.db_manager import db
from datetime import datetime
from core.data_signals import data_signals

class ReturnsPage(QWidget):
    """Page de gestion des retours"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_sale = None
        self.return_items = {}  # {product_id: quantity_to_return}
        self.init_ui()
        # Connect to language change
        i18n_manager.language_changed.connect(self.update_ui_text)
        
        # Connect signals
        data_signals.returns_changed.connect(self.load_history_data)
        data_signals.sales_changed.connect(self.load_history_data)

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
        _ = i18n_manager.get
        # Save state if needed (optional, here we might reset search but that's acceptable)
        
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
        
        # Restore state if current sale exists
        if self.current_sale:
            self.load_sale_details(self.current_sale)

    def build_ui_content(self, parent_widget):
        _ = i18n_manager.get
        layout = QVBoxLayout(parent_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        title = QLabel(_('returns_title'))
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; background: transparent;")
        
        subtitle = QLabel(_('returns_subtitle'))
        subtitle.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.9); background: transparent;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #f3f4f6;
                color: #4b5563;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #10b981;
                border-bottom: 2px solid #10b981;
            }
        """)
        
        # Tab 1: Nouveau Retour
        self.tab_new_return = QWidget()
        self.setup_new_return_tab(self.tab_new_return)
        self.tabs.addTab(self.tab_new_return, _("tab_new_return"))
        
        # Tab 2: Historique
        self.tab_history = QWidget()
        self.setup_history_tab(self.tab_history)
        self.tabs.addTab(self.tab_history, _("tab_history_returns"))
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tabs)

    def setup_new_return_tab(self, parent):
        _ = i18n_manager.get
        layout = QVBoxLayout(parent)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_('placeholder_search_return'))
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
        self.search_input.returnPressed.connect(self.search_sale)
        toolbar.addWidget(self.search_input)
        
        search_btn = QPushButton(_('btn_search_return'))
        search_btn.setMinimumHeight(50)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setStyleSheet("""
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
        search_btn.clicked.connect(self.search_sale)
        toolbar.addWidget(search_btn)
        
        layout.addLayout(toolbar)

        # Info vente et Actions
        self.info_frame = QFrame()
        self.info_frame.setVisible(False)
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border-radius: 12px;
                border: 1px solid #bbf7d0;
            }
        """)
        info_layout = QHBoxLayout(self.info_frame)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        self.sale_info_label = QLabel()
        self.sale_info_label.setStyleSheet("font-size: 16px; color: #15803d; font-weight: bold;")
        
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
        self.items_table.setAlternatingRowColors(True)
        self.items_table.verticalHeader().setDefaultSectionSize(50)
        self.items_table.setStyleSheet("""
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
        
    def setup_history_tab(self, parent):
        _ = i18n_manager.get
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Actions Layout (Refresh, Reprint)
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton(_("btn_refresh"))
        refresh_btn.setStyleSheet("padding: 5px 15px; border-radius: 5px; background-color: #e5e7eb;")
        refresh_btn.clicked.connect(self.load_history_data)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        
        self.btn_reprint_history = QPushButton(_("btn_reprint_ticket_history"))
        self.btn_reprint_history.setEnabled(False)
        self.btn_reprint_history.setStyleSheet("""
            QPushButton {
                background-color: #64748b; color: white; padding: 8px 15px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:disabled { background-color: #cbd5e1; }
        """)
        self.btn_reprint_history.clicked.connect(self.reprint_return_ticket)
        actions_layout.addWidget(self.btn_reprint_history)
        
        layout.addLayout(actions_layout)
        
        # Table History
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(_("table_history_headers_returns"))
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setStyleSheet(self.items_table.styleSheet()) # Same style
        
        self.history_table.itemSelectionChanged.connect(self.on_history_selection_changed)
        
        layout.addWidget(self.history_table)

    def on_tab_changed(self, index):
        if index == 1: # History tab
            self.load_history_data()
        elif index == 0:
            if hasattr(self, 'search_input'):
                self.search_input.setFocus()

    def load_history_data(self):
        try:
            query = """
                SELECT r.id, r.return_number, s.sale_number, r.return_date, r.return_amount, 
                       u.full_name, r.reason
                FROM returns r
                JOIN sales s ON r.original_sale_id = s.id
                JOIN users u ON r.processed_by = u.id
                ORDER BY r.return_date DESC
                LIMIT 50
            """
            returns = db.execute_query(query)
            
            self.history_table.setRowCount(0)
            for row, r in enumerate(returns):
                self.history_table.insertRow(row)
                
                # Store ID in hidden item or user data
                id_item = QTableWidgetItem(r['return_number'])
                id_item.setData(Qt.UserRole, r['id'])
                
                self.history_table.setItem(row, 0, id_item)
                self.history_table.setItem(row, 1, QTableWidgetItem(r['sale_number']))
                self.history_table.setItem(row, 2, QTableWidgetItem(str(r['return_date'])))
                self.history_table.setItem(row, 3, QTableWidgetItem(f"{r['return_amount']:.2f} DA"))
                self.history_table.setItem(row, 4, QTableWidgetItem(r['full_name']))
                self.history_table.setItem(row, 5, QTableWidgetItem(r['reason'] or ""))
                
            self.btn_reprint_history.setEnabled(False)
            
        except Exception as e:
            logger.error(f"Erreur chargement historique retours: {e}")

    def on_history_selection_changed(self):
        selected = self.history_table.selectedItems()
        self.btn_reprint_history.setEnabled(len(selected) > 0)

    def reprint_return_ticket(self):
        selected_row = self.history_table.currentRow()
        if selected_row < 0:
            return
            
        return_id = self.history_table.item(selected_row, 0).data(Qt.UserRole)
        
        try:
            return_data = pos_manager.get_return(return_id)
            if return_data:
                printer_manager.print_return_ticket(return_data)
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de récupérer les données du retour.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'impression: {e}")

    def reset_ui(self):
        """Réinitialiser l'interface à l'état par défaut"""
        self.current_sale = None
        self.return_items = {}
        self.search_input.clear()
        self.items_table.setRowCount(0)
        self.info_frame.hide()
        self.items_table.hide()
        self.btn_process_return.setEnabled(False)
        self.btn_cancel_all.setEnabled(False)
        self.btn_reprint.setEnabled(False)
        self.sale_info_label.setText("")
        self.search_input.setFocus()
        self.search_input.setFocus()

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
        
        # Switch to first tab when loading a sale
        self.tabs.setCurrentIndex(0)
        
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
        
        # Show items table
        self.items_table.setVisible(True)

        # Charger items (Seulement ceux avec quantité > 0)
        items = db.execute_query("""
            SELECT si.*, p.name as product_name 
            FROM sale_items si 
            JOIN products p ON si.product_id = p.id 
            WHERE si.sale_id = ? AND si.quantity > 0.001
        """, (sale['id'],))
        
        self.items_table.setRowCount(0)
        if not items:
            QMessageBox.information(self, _('title_info'), "Tous les articles de cette vente ont déjà été retournés.")
            return

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
            qty_spin.setRange(0, int(item['quantity']))
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
        tr = i18n_manager.get
        if not self.return_items:
            QMessageBox.warning(self, tr('title_warning'), tr('msg_select_items_return'))
            return
            
        reply = QMessageBox.question(self, tr('title_confirm'), 
                                   tr('msg_confirm_partial_return'),
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            # Use pos_manager for return processing
            user = auth_manager.get_current_user()
            user_id = user['id'] if user else 1 # Default to 1 if no user logged in
            
            # Convert return_items dict to list of {'product_id': id, 'quantity': qty}
            items_for_manager = [{'product_id': pid, 'quantity': qty} for pid, qty in self.return_items.items()]

            success, msg, return_id = pos_manager.process_return(
                self.current_sale['id'], items_for_manager, user_id, "Retour partiel client"
            )
            
            if success:
                QMessageBox.information(self, tr('title_success'), msg)
                
                # Proposer d'imprimer le ticket de retour
                print_reply = QMessageBox.question(
                    self, tr('title_confirm'),
                    "Voulez-vous imprimer un ticket de retour ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if print_reply == QMessageBox.Yes and return_id:
                     # Récupérer les données du retour
                    return_data = pos_manager.get_return(return_id)
                    if return_data:
                        from modules.sales.printer import printer_manager
                        printer_manager.print_return_ticket(return_data)
                
                self.reset_ui() # Reset UI instead of staying on ticket
            else:
                QMessageBox.critical(self, tr('title_error'), msg)

        except Exception as e:
            logger.error(f"Erreur retour: {e}")
            QMessageBox.critical(self, tr('title_error'), f"{e}")

    def cancel_entire_sale(self):
        _ = i18n_manager.get
        if not auth_manager.check_permission('cancel_sales'):
            QMessageBox.warning(self, _('title_error'), "Permission requise: cancel_sales")
            return

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
        if hasattr(self, 'search_input'):
            self.search_input.setFocus()
        if self.current_sale:
            self.search_sale() # Actualiser les données de la vente affichée
