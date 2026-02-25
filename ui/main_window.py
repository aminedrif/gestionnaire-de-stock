# -*- coding: utf-8 -*-
"""
Fenêtre principale de l'application
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QMessageBox,
                             QStatusBar, QToolBar, QComboBox, QFrame, QApplication, QShortcut, 
                             QScrollArea, QInputDialog, QLineEdit, QSizePolicy, QAbstractScrollArea)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QKeySequence, QPixmap
from core.auth import auth_manager
from core.logger import logger
from core.i18n import i18n_manager
import os
from ui.home_page import HomePage
from ui.pos_page import POSPage
from ui.products_page import ProductsPage
from ui.customers_page import CustomersPage
from ui.suppliers_page import SuppliersPage
from ui.reports_page import ReportsPage
from ui.settings_page import SettingsPage
from ui.returns_page import ReturnsPage
from ui.sales_history_page import SalesHistoryPage
from ui.categories_page import CategoriesPage
from ui.shortcuts_mgmt_page import ShortcutsManagementPage

import config


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_widget = None
        self.is_dark_mode = False
        self.page_map = {} # Pour stocker les références des pages
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"{config.APP_NAME} - {user_data['full_name']}")
        self.setGeometry(100, 100, 1280, 720)
        
        # Initialiser l'UI
        self.init_ui()
        
        # Créer raccourcis
        self.create_shortcuts()
        
        # Créer la barre d'outils
        self.create_toolbar()
        
        # Démarrer le timer pour l'horloge
        self.start_clock()
        
        # Appliquer le style initial
        self.apply_theme()
        
        logger.info(f"Fenêtre principale ouverte pour {user_data['username']}")
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Set Layout Direction based on Language
        if i18n_manager.is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Menu latéral
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Zone de contenu
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)
        
        # Ajouter les pages
        self.add_pages()
        
        central_widget.setLayout(main_layout)
        
        # Barre de statut
        self.create_status_bar()
    
    def create_sidebar(self):
        """Créer le menu latéral avec design moderne"""
        # Conteneur principal fixe (non scrollable globalement)
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(250)
        
        # Style global du sidebar
        self.sidebar_style = """
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #34495e
                );
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
        """
        self.sidebar_container.setStyleSheet(self.sidebar_style)
        
        # Layout principal vertical
        self.sidebar_layout = QVBoxLayout(self.sidebar_container)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        # 1. Zone Menu (Scrollable)
        self.menu_scroll_area = QScrollArea()
        self.menu_scroll_area.setWidgetResizable(True)
        self.menu_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu_scroll_area.setFrameShape(QFrame.NoFrame)
        # Fond transparent pour le scroll area
        self.menu_scroll_area.setStyleSheet("background: transparent;")
        # Prevent scroll area from forcing window height expansion
        self.menu_scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.menu_scroll_area.setMinimumHeight(0)
        self.menu_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        
        self.sidebar_layout.addWidget(self.menu_scroll_area)
        
        # 2. Zone Footer (Fixe en bas)
        self.footer_widget = QWidget()
        self.footer_widget.setStyleSheet("background: transparent;")
        self.footer_widget.setMaximumHeight(120)  # Prevent excessive height calculation
        self.sidebar_layout.addWidget(self.footer_widget)
        
        # Build content
        self.build_sidebar_content()
        
        return self.sidebar_container

    def build_sidebar_content(self):
        """Construire le contenu du menu latéral"""
        _ = i18n_manager.get
        
        # --- Construction du Menu (Scrollable) ---
        self.menu_content = QWidget()
        self.menu_content.setStyleSheet("background: transparent;")
        
        menu_layout = QVBoxLayout(self.menu_content)
        menu_layout.setSpacing(4)
        menu_layout.setContentsMargins(0, 10, 0, 10)
        
        # Logo/Titre
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        
        logo_path = str(config.LOGO_PATH)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🏪")
            logo_label.setStyleSheet("font-size: 50px; background: transparent; border: none;")
            
        menu_layout.addWidget(logo_label)
        
        title_label = QLabel(_('app_title'))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 4px; background: transparent; border: none;")
        menu_layout.addWidget(title_label)
        
        menu_layout.addSpacing(15)
        
        # Boutons de menu
        self.menu_buttons = {}
        
        btn_home = self.create_menu_button(_('menu_home'), "home")
        menu_layout.addWidget(btn_home)
        self.menu_buttons['home'] = btn_home
        
        btn_pos = self.create_menu_button(_('menu_pos'), "pos")
        menu_layout.addWidget(btn_pos)
        self.menu_buttons['pos'] = btn_pos
        
        if auth_manager.has_permission('manage_products'):
            btn_products = self.create_menu_button(_('menu_products'), "products")
            menu_layout.addWidget(btn_products)
            self.menu_buttons['products'] = btn_products

            btn_categories = self.create_menu_button(_('menu_categories'), "categories")
            menu_layout.addWidget(btn_categories)
            self.menu_buttons['categories'] = btn_categories

        # Shortcuts Mgmt (Moved under Products as requested)
        if auth_manager.has_permission('manage_shortcuts'):
            btn_shortcuts = self.create_menu_button("⚡ Raccourcis", "shortcuts_mgmt")
            menu_layout.addWidget(btn_shortcuts)
            self.menu_buttons['shortcuts_mgmt'] = btn_shortcuts
        
        if auth_manager.has_permission('view_customers'):
            btn_customers = self.create_menu_button(_('menu_customers'), "customers")
            menu_layout.addWidget(btn_customers)
            self.menu_buttons['customers'] = btn_customers
        
        if auth_manager.has_permission('manage_suppliers'):
            btn_suppliers = self.create_menu_button(_('menu_suppliers'), "suppliers")
            menu_layout.addWidget(btn_suppliers)
            self.menu_buttons['suppliers'] = btn_suppliers
        
        if auth_manager.has_permission('view_reports'):
            btn_reports = self.create_menu_button(_('menu_reports'), "reports")
            menu_layout.addWidget(btn_reports)
            self.menu_buttons['reports'] = btn_reports



        if auth_manager.has_permission('process_returns'):
            btn_returns = self.create_menu_button(_('menu_returns'), "returns")
            menu_layout.addWidget(btn_returns)
            self.menu_buttons['returns'] = btn_returns

        if auth_manager.has_permission('view_sales_history'):
            btn_history = self.create_menu_button(_('menu_history'), "history")
            menu_layout.addWidget(btn_history)
            self.menu_buttons['history'] = btn_history
        

        
        # Settings
        if auth_manager.has_permission('manage_settings'):
            btn_settings = self.create_menu_button(_('menu_settings'), "settings")
            menu_layout.addWidget(btn_settings)
            self.menu_buttons['settings'] = btn_settings


        
        menu_layout.addStretch() # Push menu items up
        
        self.menu_scroll_area.setWidget(self.menu_content)
        
        # --- Construction du Footer (Fixe) ---
        # Check if footer already has a layout (during language toggle rebuild)
        footer_layout = self.footer_widget.layout()
        if footer_layout is None:
            footer_layout = QVBoxLayout(self.footer_widget)
            footer_layout.setContentsMargins(0, 10, 0, 10)
            footer_layout.setSpacing(5)
        
        # Language Switch Button
        self.lang_btn = QPushButton(f"🌐 {i18n_manager.current_language.upper()}")
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 10px;
                border-radius: 8px;
                margin: 0px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(139, 92, 246, 0.5);
                border-color: #8b5cf6;
            }
        """)
        self.lang_btn.clicked.connect(self.toggle_language)
        footer_layout.addWidget(self.lang_btn)

        # Bouton déconnexion
        btn_logout = QPushButton(_('menu_logout'))
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 10px;
                border-radius: 5px;
                margin: 0px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        footer_layout.addWidget(btn_logout)
        
        # Restore checked state...
        
        # Restore checked state if current page is set
        if hasattr(self, 'content_area') and hasattr(self, 'current_widget') and self.content_area.currentWidget():
            # Iterate to find which page is active based on logical mapping
            for name, page in self.page_map.items():
                if page == self.content_area.currentWidget():
                     if name in self.menu_buttons:
                         self.menu_buttons[name].setChecked(True)
                     break
    
    def create_menu_button(self, text, page_name):
        """Créer un bouton de menu avec design moderne"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setMinimumHeight(45)
        button.setCursor(Qt.PointingHandCursor)
        
        # Text Align: Left for LTR, Right for RTL?
        # Actually in RTL mode, "padding-left" might need to be "padding-right"
        # Since we use `setLayoutDirection(Qt.RightToLeft)`, Qt handles the "Start" alignment.
        # But CSS 'text-align: left' is explicit.
        # Let's use 'text-align: left' for both for now (as icons are often on the left/start).
        # In RTL, 'text-align: left' puts text on the LEFT. We want Start.
        # But since we set LayoutDirection on MainWindow, maybe we don't need text-align?
        # QPushButton default alignment is usually centered.
        
        align = "right" if i18n_manager.is_rtl() else "left"
        padding = "padding-right: 25px;" if i18n_manager.is_rtl() else "padding-left: 25px;"
        border = "border-right" if i18n_manager.is_rtl() else "border-left"

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(255, 255, 255, 0.9);
                border: none;
                {border}: 4px solid transparent;
                border-radius: 0px;
                {padding}
                text-align: {align};
                font-size: 15px;
                font-weight: 500;
                margin: 2px 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.12);
                {border}: 4px solid rgba(139, 92, 246, 0.6);
                color: white;
            }}
            QPushButton:checked {{
                background-color: rgba(139, 92, 246, 0.3);
                {border}: 4px solid #8b5cf6;
                color: white;
                font-weight: bold;
            }}
        """)
        button.clicked.connect(lambda: self.switch_page(page_name))
        return button
    
    def create_shortcuts(self):
        """Créer les raccourcis clavier"""
        shortcuts = [
            ("F1", "home"),
            ("F2", "pos"),
            ("F3", "products"),
            ("F4", "customers"),
            ("F5", "suppliers"),
            ("F7", "returns"),
            ("F8", "history"),
            ("F9", "shortcuts_mgmt"),
            ("F10", "settings"),
        ]
        
        for key, page in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            # Utilisation de lambda avec un argument par défaut pour capturer la valeur
            shortcut.activated.connect(lambda p=page: self.switch_page(p))
            
    def add_pages(self):
        """Ajouter les pages au contenu"""
        self.page_map = {}
        
        # Page d'accueil
        self.home_page = HomePage()
        self.home_page.navigate_to.connect(self.switch_page)
        self.home_page.quick_scan.connect(self.handle_quick_scan)
        self.content_area.addWidget(self.home_page)
        self.page_map['home'] = self.home_page
        
        # Caisse (toujours disponible)
        self.pos_page = POSPage()
        self.content_area.addWidget(self.pos_page)
        self.page_map['pos'] = self.pos_page
        
        # Produits
        if auth_manager.has_permission('manage_products'):
            products_page = ProductsPage()
            self.content_area.addWidget(products_page)
            self.page_map['products'] = products_page

            categories_page = CategoriesPage()
            self.content_area.addWidget(categories_page)
            self.page_map['categories'] = categories_page
        
        # Clients
        if auth_manager.has_permission('view_customers'):
            self.customers_page = CustomersPage()
            self.customers_page.navigate_to.connect(self.switch_page)
            self.content_area.addWidget(self.customers_page)
            self.page_map['customers'] = self.customers_page
        
        # Fournisseurs
        if auth_manager.has_permission('manage_suppliers'):
            suppliers_page = SuppliersPage()
            self.content_area.addWidget(suppliers_page)
            self.page_map['suppliers'] = suppliers_page
        
        # Rapports
        if auth_manager.has_permission('view_reports'):
            reports_page = ReportsPage()
            self.content_area.addWidget(reports_page)
            self.page_map['reports'] = reports_page
            

            
        # Retours
        if auth_manager.has_permission('process_returns'):
            self.returns_page = ReturnsPage()
            self.content_area.addWidget(self.returns_page)
            self.page_map['returns'] = self.returns_page

        # Historique (Accessible à tous) -> (Maintenant restreint)
        if auth_manager.has_permission('view_sales_history'):
            self.history_page = SalesHistoryPage()
            self.history_page.navigate_to.connect(self.switch_page)
            self.content_area.addWidget(self.history_page)
            self.page_map['history'] = self.history_page
        
        # Gestion des Raccourcis
        if auth_manager.has_permission('manage_shortcuts'):
            self.shortcuts_mgmt_page = ShortcutsManagementPage()
            self.content_area.addWidget(self.shortcuts_mgmt_page)
            self.page_map['shortcuts_mgmt'] = self.shortcuts_mgmt_page
        
        # Paramètres
        if auth_manager.has_permission('manage_settings'):
            self.settings_page = SettingsPage()
            self.content_area.addWidget(self.settings_page)
            self.page_map['settings'] = self.settings_page
    
    def handle_quick_scan(self, barcode):
        """Gérer le scan rapide depuis l'accueil"""
        # Basculer vers Caisse
        self.switch_page('pos')
        # Ajouter le produit
        self.pos_page.barcode_input.setText(barcode)
        self.pos_page.scan_product()
    
    def switch_page(self, page_name, nav_data=None):
        """Changer de page"""
        # Handle special case for products with low stock filter
        filter_low_stock = False
        actual_page = page_name
        if page_name == "products_low_stock":
            actual_page = "products"
            filter_low_stock = True
            
        if actual_page == "cashier_window" or actual_page == "pos":
            from ui.cashier_window import CashierWindow
            # Only create new if not exists or maybe multiple? 
            # Usually one POS window.
            if not hasattr(self, 'cashier_window') or not self.cashier_window.isVisible():
                self.cashier_window = CashierWindow(self)
                self.cashier_window.showMaximized()
            else:
                self.cashier_window.activateWindow()
            return

        if actual_page in self.page_map:
            target_widget = self.page_map[actual_page]
            self.content_area.setCurrentWidget(target_widget)
            
            # Rafraîchir les données si la page le supporte
            if hasattr(target_widget, 'refresh'):
                target_widget.refresh()
                
            # Application de filtres spécifiques si fournis dans nav_data
            if nav_data:
                if actual_page == 'history' and 'filter_customer' in nav_data:
                    if hasattr(target_widget, 'filter_by_customer'):
                        target_widget.filter_by_customer(nav_data['filter_customer'])
                elif actual_page == 'returns' and 'load_sale' in nav_data:
                    if hasattr(target_widget, 'load_sale_external'):
                        target_widget.load_sale_external(nav_data['load_sale'])
                        
            # Apply low stock filter if needed
            if filter_low_stock and hasattr(target_widget, 'filter_combo'):
                # Find and select "Stock faible" option
                for i in range(target_widget.filter_combo.count()):
                    if "faible" in target_widget.filter_combo.itemText(i).lower():
                        target_widget.filter_combo.setCurrentIndex(i)
                        break
            
            # Mettre à jour les boutons
            for name, button in self.menu_buttons.items():
                button.setChecked(name == actual_page)
                
            logger.info(f"Navigation vers: {actual_page}")
        else:
            logger.warning(f"Page non disponible ou droits insuffisants: {page_name}")
    
    def create_toolbar(self):
        """Créer la barre d'outils"""
        pass
        
    def create_status_bar(self):
        """Créer la barre de statut"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.clock_label = QLabel()
        self.statusBar.addPermanentWidget(self.clock_label)
    
    def start_clock(self):
        """Démarrer l'horloge"""
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
    
    def update_clock(self):
        current_time = QDateTime.currentDateTime()
        self.clock_label.setText(current_time.toString("dddd dd MMMM yyyy - HH:mm:ss"))
    
    def apply_theme(self):
        """Appliquer le thème clair à l'application"""
        app = QApplication.instance()
        
        # Thème clair uniquement
        app.setStyle("Fusion")
        palette = QPalette()
        
        # Couleurs de base claires
        light_bg = QColor(245, 245, 245)  # #f5f5f5
        light_base = QColor(255, 255, 255)  # white
        light_alt = QColor(248, 249, 250)  # #f8f9fa
        dark_text = QColor(44, 62, 80)  # #2c3e50
        accent = QColor(52, 152, 219)  # #3498db
        
        palette.setColor(QPalette.Window, light_bg)
        palette.setColor(QPalette.WindowText, dark_text)
        palette.setColor(QPalette.Base, light_base)
        palette.setColor(QPalette.AlternateBase, light_alt)
        palette.setColor(QPalette.ToolTipBase, dark_text)
        palette.setColor(QPalette.ToolTipText, light_base)
        palette.setColor(QPalette.Text, dark_text)
        palette.setColor(QPalette.Button, light_bg)
        palette.setColor(QPalette.ButtonText, dark_text)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, accent)
        palette.setColor(QPalette.Highlight, accent)
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        app.setPalette(palette)
        
        # Réinitialiser le style
        self.content_area.setStyleSheet("")
        
        # Sidebar style
        if hasattr(self, 'sidebar_content'):
            self.sidebar_content.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c3e50, stop:1 #34495e);
                }
            """)
        
    def toggle_language(self):
        """Toggle between French and Arabic"""
        i18n_manager.toggle_language()
        
        # Update layout direction
        if i18n_manager.is_rtl():
             self.setLayoutDirection(Qt.RightToLeft)
        else:
             self.setLayoutDirection(Qt.LeftToRight)
        
        # Completely destroy and recreate footer widget for clean rebuild
        if hasattr(self, 'footer_widget') and self.footer_widget:
            # Remove from parent layout
            self.sidebar_layout.removeWidget(self.footer_widget)
            # Delete the widget and all its children
            self.footer_widget.deleteLater()
            
            # Create new footer widget
            self.footer_widget = QWidget()
            self.footer_widget.setStyleSheet("background: transparent;")
            self.footer_widget.setMaximumHeight(120)  # Prevent excessive height calculation
            self.sidebar_layout.addWidget(self.footer_widget)
                
        # Rebuild sidebar
        self.build_sidebar_content()
        
        # Update all pages that support language changes
        for page in self.page_map.values():
            if hasattr(page, 'update_ui_text'):
                try:
                    page.update_ui_text()
                except Exception as e:
                    logger.error(f"Error updating page text: {e}")
        
        # Force layout refresh to ensure buttons appear correctly
        QTimer.singleShot(100, self.force_layout_refresh)
        
        logger.info(f"Language switched to: {i18n_manager.current_language}")


        



    def force_layout_refresh(self):
        """Force a layout update without resizing the window"""
        # Process pending events to ensure widget deletions are complete
        QApplication.processEvents()
        
        # Force update on key sidebar widgets
        if hasattr(self, 'footer_widget') and self.footer_widget:
            self.footer_widget.updateGeometry()
            self.footer_widget.repaint()
        if hasattr(self, 'menu_content') and self.menu_content:
            self.menu_content.updateGeometry()
            self.menu_content.repaint()
        if hasattr(self, 'sidebar_container') and self.sidebar_container:
            self.sidebar_container.updateGeometry()
            self.sidebar_container.repaint()
        
        # Force the main window to recalculate layout
        self.updateGeometry()
        self.repaint()


    def logout(self):
        _ = i18n_manager.get
        reply = QMessageBox.question(self, _('confirm_logout_title'), _('confirm_logout_msg'), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            auth_manager.logout()
            self.close()
