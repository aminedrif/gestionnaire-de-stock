# -*- coding: utf-8 -*-
"""
Dialogue de configuration des raccourcis POS
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QDoubleSpinBox,
                             QComboBox, QFileDialog, QMessageBox, QGroupBox,
                             QFormLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QPixmap, QFont, QIcon
from pathlib import Path
import shutil

from modules.products.product_manager import product_manager
from modules.sales.shortcuts_manager import shortcuts_manager
from database.db_manager import db
from core.i18n import i18n_manager
from core.logger import logger
import config

# Helper for translation
def _(key):
    return i18n_manager.get(key)

class ShortcutConfigDialog(QDialog):
    """Dialogue de configuration d'un raccourci POS"""
    
    def __init__(self, shortcut_id=None, position=None, parent=None):
        """
        Initialiser le dialogue
        
        Args:
            shortcut_id: ID du raccourci à éditer (None pour nouveau)
            position: Position suggérée pour nouveau raccourci
            parent: Widget parent
        """
        super().__init__(parent)
        self.shortcut_id = shortcut_id
        self.suggested_position = position
        self.current_image_path = None
        self.shortcut_data = None
        
        # Charger les données si édition
        if shortcut_id:
            self.shortcut_data = shortcuts_manager.get_shortcut(shortcut_id)
        
        self.setup_ui()
        
        # Charger les données si édition
        if self.shortcut_data:
            self.load_shortcut_data()
            
        # Focus on barcode input by default
        self.barcode_input.setFocus()
    
    def setup_ui(self):
        """Configurer l'interface"""
        title = _('shortcut_edit_title') if self.shortcut_id else _('shortcut_new_title')
        
        self.setWindowTitle(title)
        self.setMinimumWidth(550)
        self.setMinimumHeight(650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel(title)
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Formulaire
        form_group = QGroupBox(_('config_section'))
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #8b5cf6;
                subcontrol-position: top left;
                padding: 5px 10px;
            }
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # 1. Scan Barcode (New)
        scan_layout = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText(_('scan_barcode_placeholder'))
        self.barcode_input.setMinimumHeight(40)
        self.barcode_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        self.barcode_input.returnPressed.connect(self.on_barcode_scanned)
        
        scan_btn = QPushButton("🔍")
        scan_btn.setToolTip("Rechercher")
        scan_btn.setFixedSize(40, 40)
        scan_btn.clicked.connect(self.on_barcode_scanned)
        
        scan_layout.addWidget(self.barcode_input)
        scan_layout.addWidget(scan_btn)
        form_layout.addRow(_('barcode_label'), scan_layout)
        
        # 2. Sélection du produit (Searchable Combo)
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)  # Enable typing to search
        self.product_combo.setInsertPolicy(QComboBox.NoInsert)  # Don't add typed text as new item
        self.product_combo.setMinimumHeight(40)
        self.product_combo.lineEdit().setPlaceholderText("🔍 Tapez pour rechercher un produit...")
        self.product_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
            }
        """)
        self.load_products()
        
        # Add completer for better search
        completer = self.product_combo.completer()
        if completer:
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setFilterMode(Qt.MatchContains)  # Search anywhere in string
        
        form_layout.addRow(_('product_label'), self.product_combo)
        
        
        # 4. Libellé personnalisé
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Ex: Farha , Amir fromage, Coca 500ml...")
        self.label_input.setMinimumHeight(40)
        self.label_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        form_layout.addRow(_('label_input_label'), self.label_input)
        
        # 5. Prix unitaire
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(" DA")
        self.price_input.setMinimumHeight(40)
        self.price_input.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        form_layout.addRow(_('price_label'), self.price_input)
        
        # Autocompléter le prix depuis le produit sélectionné
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Section Image
        image_group = QGroupBox(_('image_section'))
        image_group.setStyleSheet(form_group.styleSheet())
        image_layout = QVBoxLayout()
        
        # Aperçu de l'image (Larger preview that fills the box)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(150, 150)  # Larger preview
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setScaledContents(True)  # Fill the box
        self.image_preview.setStyleSheet("""
            border: 2px dashed #ccc;
            border-radius: 8px;
            background-color: #f9fafb;
        """)
        self.image_preview.setText("🖼️")
        image_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)
        
        # Boutons image
        image_btn_layout = QHBoxLayout()
        
        upload_btn = QPushButton(_('btn_upload'))
        upload_btn.clicked.connect(self.upload_image)
        image_btn_layout.addWidget(upload_btn)
        
        clear_img_btn = QPushButton(_('btn_clear'))
        clear_img_btn.clicked.connect(self.clear_image)
        image_btn_layout.addWidget(clear_img_btn)
        
        image_layout.addLayout(image_btn_layout)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        layout.addStretch()
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton(_('btn_save'))
        save_btn.setMinimumHeight(50)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_shortcut)
        btn_layout.addWidget(save_btn)
        
        if self.shortcut_id:
            delete_btn = QPushButton(_('btn_delete'))
            delete_btn.setMinimumHeight(50)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(self.delete_shortcut)
            btn_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton(_('btn_cancel'))
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def load_products(self):
        """Charger la liste des produits"""
        try:
            products = product_manager.get_all_products()
            
            self.product_combo.clear()
            self.product_combo.addItem("", None)
            
            for product in products:
                display_text = f"{product['name']} - {product['selling_price']:.2f} DA"
                if product['barcode']:
                    display_text = f"[{product['barcode']}] " + display_text
                
                self.product_combo.addItem(display_text, product)
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des produits: {e}")
            

    def on_barcode_scanned(self):
        """Gérer le scan de code-barres"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        product = product_manager.get_product_by_barcode(barcode)
        if product:
            # Find and select in combo
            index = -1
            for i in range(self.product_combo.count()):
                data = self.product_combo.itemData(i)
                if data and data['id'] == product['id']:
                    index = i
                    break
            
            if index >= 0:
                self.product_combo.setCurrentIndex(index)
                self.barcode_input.clear()
            else:
                 QMessageBox.warning(self, "Info", "Produit trouvé mais non listé (archivé?)")
        else:
            QMessageBox.warning(self, "Erreur", "Aucun produit trouvé avec ce code-barres")
            self.barcode_input.selectAll()
    
    def on_product_selected(self, index):
        """Gérer la sélection d'un produit"""
        if index <= 0:
            return
            
        product = self.product_combo.currentData()
        if product:
            # Remplir automatiquement le libellé si vide
            if not self.label_input.text():
                self.label_input.setText(product['name'])
            
            # Remplir le prix
            self.price_input.setValue(product['selling_price'])
            
    def upload_image(self):
        """Charger une image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                # Créer le dossier d'images des raccourcis s'il n'existe pas
                shortcuts_dir = config.DATA_DIR / "shortcuts_images"
                shortcuts_dir.mkdir(exist_ok=True)
                
                # Copier l'image avec un nom unique
                source = Path(file_path)
                dest = shortcuts_dir / f"shortcut_{source.name}"
                
                shutil.copy2(source, dest)
                self.current_image_path = str(dest)
                
                # Afficher l'aperçu
                pixmap = QPixmap(str(dest))
                scaled_pixmap = pixmap.scaled(
                    120, 120, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'image: {e}")
                QMessageBox.warning(self, "Erreur", f"Impossible de charger l'image: {str(e)}")
    
    def clear_image(self):
        """Effacer l'image"""
        self.current_image_path = None
        self.image_preview.clear()
        self.image_preview.setText("🖼️")
    
    def load_shortcut_data(self):
        """Charger les données du raccourci à éditer"""
        if not self.shortcut_data:
            return
        
        # Sélectionner le produit
        if self.shortcut_data['product_id']:
            for i in range(self.product_combo.count()):
                product = self.product_combo.itemData(i)
                if product and product['id'] == self.shortcut_data['product_id']:
                    self.product_combo.setCurrentIndex(i)
                    break
        else:
            self.product_combo.setCurrentIndex(0) # Custom
        

        # Remplir les champs
        self.label_input.setText(self.shortcut_data['label'])
        self.price_input.setValue(self.shortcut_data['unit_price'])
        
        # Charger l'image si elle existe
        if self.shortcut_data['image_path']:
            image_path = Path(self.shortcut_data['image_path'])
            if image_path.exists():
                self.current_image_path = str(image_path)
                pixmap = QPixmap(str(image_path))
                scaled_pixmap = pixmap.scaled(
                    120, 120, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
    
    def save_shortcut(self):
        """Enregistrer le raccourci"""
        # Validation
        label = self.label_input.text().strip()
        if not label:
            QMessageBox.warning(self, "Validation", "Le libellé est obligatoire")
            return
        
        price = self.price_input.value()
        if price <= 0:
            QMessageBox.warning(self, "Validation", "Le prix doit être supérieur à 0")
            return
        
        # Récupérer données
        product = self.product_combo.currentData()
        product_id = product['id'] if product else None
        
        try:
            if self.shortcut_id:
                # Mise à jour
                success, msg = shortcuts_manager.update_shortcut(
                    self.shortcut_id,
                    product_id=product_id,
                    label=label,
                    image_path=self.current_image_path,
                    unit_price=price
                )
            else:
                # Création
                position = self.suggested_position or shortcuts_manager.get_next_available_position()
                success, msg, _ = shortcuts_manager.add_shortcut(
                    product_id,
                    label,
                    self.current_image_path,
                    price,
                    position
                )
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", msg)
        
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def delete_shortcut(self):
        """Supprimer le raccourci"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            _('confirm_delete_shortcut'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = shortcuts_manager.delete_shortcut(self.shortcut_id)
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", msg)
