from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QGridLayout, QFrame,
                             QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont
from modules.sales.shortcuts_manager import shortcuts_manager
from ui.shortcut_config_dialog import ShortcutConfigDialog
from database.db_manager import db
from core.i18n import i18n_manager
from core.auth import auth_manager
from core.data_signals import data_signals
from pathlib import Path
import math

# Helper for translation
def _(key):
    return i18n_manager.get(key)

class ShortcutCard(QFrame):
    """Carte visuelle pour un raccourci"""
    
    # Signals for actions
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    
    def __init__(self, shortcut, category_name, parent=None):
        super().__init__(parent)
        self.shortcut = shortcut
        self.category_name = category_name
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(160, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Position Badge (Top Right)
        top_layout = QHBoxLayout()
        pos_label = QLabel(f"#{self.shortcut['position']}")
        pos_label.setStyleSheet("""
            background-color: #f3f4f6;
            color: #6b7280;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: bold;
        """)
        top_layout.addWidget(pos_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Image
        img_label = QLabel()
        img_label.setFixedSize(60, 60)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("border: none; background: transparent;")
        
        if self.shortcut['image_path']:
            path = Path(self.shortcut['image_path'])
            if path.exists():
                pixmap = QPixmap(str(path)).scaled(
                    60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                img_label.setPixmap(pixmap)
            else:
                img_label.setText("📷")
        else:
             img_label.setText("📷")
             
        layout.addWidget(img_label, alignment=Qt.AlignCenter)
        
        # Libellé
        name_label = QLabel(self.shortcut['label'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("""
            font-weight: bold;
            color: #1f2937;
            font-size: 13px;
            border: none;
        """)
        layout.addWidget(name_label)
        
        # Category
        cat_label = QLabel(self.category_name)
        cat_label.setAlignment(Qt.AlignCenter)
        cat_label.setStyleSheet("""
            color: #6b7280;
            font-size: 11px;
            border: none;
        """)
        layout.addWidget(cat_label)
        
        # Price
        price_label = QLabel(f"{self.shortcut['unit_price']:.2f} DA")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("""
            color: #10b981;
            font-weight: bold;
            font-size: 12px;
            border: none;
        """)
        layout.addWidget(price_label)
        
        layout.addStretch()
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Edit Btn
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 30)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip(_("tooltip_edit"))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 15px;
                color: #2563eb;
            }
            QPushButton:hover {
                background-color: #dbeafe;
            }
        """)
        edit_btn.clicked.connect(self.request_edit)
        
        # Delete Btn
        del_btn = QPushButton("🗑️")
        del_btn.setFixedSize(30, 30)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip(_("tooltip_delete"))
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 15px;
                color: #dc2626;
            }
            QPushButton:hover {
                background-color: #fee2e2;
            }
        """)
        del_btn.clicked.connect(self.request_delete)
        
        actions_layout.addStretch()
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(del_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)

    def request_edit(self):
        """Emet le signal d'édition avec l'ID du raccourci"""
        self.edit_clicked.emit(self.shortcut['id'])

    def request_delete(self):
        """Emet le signal de suppression avec l'ID du raccourci"""
        self.delete_clicked.emit(self.shortcut['id'])

class ShortcutsManagementPage(QWidget):
    """Page de gestion des raccourcis POS (Grid View)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Connect to language change
        i18n_manager.language_changed.connect(self.update_ui_text)
        i18n_manager.language_changed.connect(self.update_ui_text)
        
        # Connect to data signals for refresh
        data_signals.products_changed.connect(self.refresh)
        data_signals.categories_changed.connect(self.refresh)
        data_signals.shortcuts_changed.connect(self.refresh)
        
        self.update_ui_text()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        title = QLabel(_('shortcuts_mgmt_title'))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        subtitle = QLabel(_('shortcuts_mgmt_subtitle'))
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        
        # Keep references for updates
        self.header_title = title
        self.header_subtitle = subtitle
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Bouton Ajouter
        self.add_btn = QPushButton(_('btn_new_shortcut'))
        self.add_btn.setFixedSize(220, 50)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #059669;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0fdf4;
            }
        """)
        self.add_btn.clicked.connect(self.add_shortcut)
        header_layout.addWidget(self.add_btn)
        
        layout.addWidget(header_frame)
        
        # Zone de défilement pour la grille
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area)
        
        self.load_shortcuts()

    def load_shortcuts(self):
        """Charger les raccourcis dans la grille"""
        # Nettoyer la grille
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        shortcuts = shortcuts_manager.get_all_shortcuts()
        
        # Pre-load categories
        categories = {}
        try:
            cat_rows = db.fetch_all("SELECT id, name FROM categories")
            categories = {row['id']: row['name'] for row in cat_rows}
        except:
            pass
            
        if not shortcuts:
            # Afficher message vide
            empty_label = QLabel(_('no_shortcuts_found'))
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #9ca3af; font-size: 16px; margin-top: 50px;")
            self.grid_layout.addWidget(empty_label, 0, 0, 1, 4) # Span
            return
            
        # Remplir la grille
        cols = 5 # Nombre de colonnes
        
        for idx, shortcut in enumerate(shortcuts):
            row = idx // cols
            col = idx % cols
            
            # Déterminer nom catégorie
            cat_name = "-"
            if shortcut.get('category_id'):
                cat_name = categories.get(shortcut['category_id'], "Inconnue")
            else:
                cat_name = "Produit"
                
            card = ShortcutCard(shortcut, cat_name)
            
            # Connect custom signals properly
            card.edit_clicked.connect(self.edit_shortcut)
            card.delete_clicked.connect(self.delete_shortcut)
            
            self.grid_layout.addWidget(card, row, col)


    def add_shortcut(self):
        if not auth_manager.check_permission('manage_shortcuts'):
            QMessageBox.warning(self, _("msg_access_denied"), _("msg_perm_required_shortcuts"))
            return
        dialog = ShortcutConfigDialog(parent=self)
        if dialog.exec_():
            self.load_shortcuts()

    def edit_shortcut(self, shortcut_id):
        if not auth_manager.check_permission('manage_shortcuts'):
            QMessageBox.warning(self, _("msg_access_denied"), _("msg_perm_required_shortcuts"))
            return
        dialog = ShortcutConfigDialog(shortcut_id=shortcut_id, parent=self)
        if dialog.exec_():
            self.load_shortcuts()

    def delete_shortcut(self, shortcut_id):
        if not auth_manager.check_permission('manage_shortcuts'):
            QMessageBox.warning(self, _("msg_access_denied"), _("msg_perm_required_shortcuts"))
            return
        reply = QMessageBox.question(self, "Confirmation", 
                                   _('confirm_delete_shortcut'),
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = shortcuts_manager.delete_shortcut(shortcut_id)
            if success:
                self.load_shortcuts()
            else:
                QMessageBox.warning(self, "Erreur", msg)
    
    def refresh(self):
        """Rafraîchir"""
        self.load_shortcuts()

    def update_ui_text(self):
        """Mettre à jour les textes et la direction"""
        _ = i18n_manager.get
        is_rtl = i18n_manager.is_rtl()
        
        # Direction
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)
        
        # Update texts
        if hasattr(self, 'header_title'):
            self.header_title.setText(_('shortcuts_mgmt_title'))
        if hasattr(self, 'header_subtitle'):
            self.header_subtitle.setText(_('shortcuts_mgmt_subtitle'))
        if hasattr(self, 'add_btn'):
            self.add_btn.setText(_('btn_new_shortcut'))
            
        # Re-load shortcuts to refresh cards (if they contain localized text)
        self.load_shortcuts()
