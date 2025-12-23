# Interface PyQt5 - Mini-Market

## 🎨 Interface Créée

### ✅ Écrans Implémentés

#### 1. Dialogue de Connexion (`ui/login_dialog.py`)

**Fonctionnalités:**
- ✅ Champs username et password
- ✅ Sélection de langue (FR/AR)
- ✅ Validation des champs
- ✅ Intégration avec le système d'authentification
- ✅ Gestion des erreurs de connexion
- ✅ Style moderne et professionnel
- ✅ Centrage automatique sur l'écran

**Utilisation:**
```python
from ui.login_dialog import LoginDialog

dialog = LoginDialog()
if dialog.exec_() == LoginDialog.Accepted:
    # Connexion réussie
    language = dialog.get_selected_language()
```

#### 2. Fenêtre Principale (`ui/main_window.py`)

**Fonctionnalités:**
- ✅ Menu latéral avec navigation
- ✅ Permissions basées sur le rôle utilisateur
- ✅ Barre de statut avec horloge en temps réel
- ✅ Pages placeholder pour tous les modules
- ✅ Bouton de déconnexion
- ✅ Confirmation avant fermeture
- ✅ Style moderne avec sidebar sombre

**Modules accessibles:**
- 🛒 **Caisse** - Tous les utilisateurs
- 📦 **Produits** - Admin + permissions
- 👥 **Clients** - Admin + permissions
- 🏭 **Fournisseurs** - Admin + permissions
- 📊 **Rapports** - Admin + permissions
- ⚙️ **Paramètres** - Admin uniquement

---

## 🚧 À Implémenter

### Pages Détaillées

#### 1. Interface Caisse (Priorité Haute)

**Fichier:** `ui/sales/pos_widget.py`

**Composants nécessaires:**
- Scanner code-barres (QLineEdit avec focus)
- Table panier (QTableWidget)
- Panneau totaux (QLabel)
- Boutons paiement (QPushButton)
- Dialogue réduction
- Aperçu ticket

**Layout suggéré:**
```
┌─────────────────────────────────────────┐
│  Scanner: [_______________] [Rechercher]│
├─────────────────────────────────────────┤
│  Panier:                                │
│  ┌───────────────────────────────────┐  │
│  │ Produit │ Qté │ Prix │ Total     │  │
│  │─────────┼─────┼──────┼───────────│  │
│  │ ...     │ ... │ ...  │ ...       │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  Sous-total:              1000.00 DA   │
│  Réduction:                -50.00 DA   │
│  TOTAL:                    950.00 DA   │
├─────────────────────────────────────────┤
│  [Espèces] [Carte] [Crédit] [Annuler]  │
└─────────────────────────────────────────┘
```

#### 2. Gestion Produits (Priorité Haute)

**Fichier:** `ui/products/products_widget.py`

**Composants:**
- Barre de recherche
- Table des produits (QTableWidget)
- Boutons CRUD
- Dialogues ajout/édition
- Filtres par catégorie

#### 3. Autres Modules (Priorité Moyenne)

- `ui/customers/customers_widget.py`
- `ui/suppliers/suppliers_widget.py`
- `ui/reports/reports_widget.py`
- `ui/settings/settings_widget.py`

---

## 🎨 Guide de Style

### Palette de Couleurs

```python
COLORS = {
    'primary': '#3498db',      # Bleu
    'success': '#4CAF50',      # Vert
    'danger': '#e74c3c',       # Rouge
    'warning': '#f39c12',      # Orange
    'dark': '#2c3e50',         # Bleu foncé
    'sidebar': '#2c3e50',      # Sidebar
    'background': '#ecf0f1',   # Fond clair
    'text': '#333333',         # Texte
}
```

### Styles CSS Qt

**Boutons:**
```css
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45a049;
}
```

**Tables:**
```css
QTableWidget {
    border: 1px solid #ddd;
    background-color: white;
    alternate-background-color: #f9f9f9;
}
QHeaderView::section {
    background-color: #3498db;
    color: white;
    padding: 8px;
    font-weight: bold;
}
```

---

## 📝 Exemple: Créer un Widget

```python
# ui/products/products_widget.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QLineEdit)
from modules.products.product_manager import product_manager

class ProductsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Code-barres", "Nom", "Catégorie", 
            "Prix", "Stock", "Actions"
        ])
        layout.addWidget(self.table)
        
        # Boutons
        button_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Ajouter")
        btn_add.clicked.connect(self.add_product)
        button_layout.addWidget(btn_add)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_products(self):
        products = product_manager.get_all_products()
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(product['barcode']))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            # ... etc
    
    def on_search(self, text):
        if text:
            products = product_manager.search_products(text)
        else:
            products = product_manager.get_all_products()
        # Mettre à jour la table
    
    def add_product(self):
        # Ouvrir dialogue d'ajout
        pass
```

---

## 🚀 Lancement de l'Interface

```bash
# Installer PyQt5
pip install PyQt5

# Lancer l'application
python main.py
```

**Connexion par défaut:**
- Username: `admin`
- Password: `admin123`

---

## 📋 Checklist Interface

### Phase 1: Base ✅
- [x] Dialogue de connexion
- [x] Fenêtre principale
- [x] Menu latéral
- [x] Barre de statut
- [x] Navigation

### Phase 2: Modules Essentiels
- [ ] Interface caisse (POS)
- [ ] Gestion produits
- [ ] Dialogues CRUD produits

### Phase 3: Modules Complémentaires
- [ ] Gestion clients
- [ ] Gestion fournisseurs
- [ ] Rapports avec graphiques

### Phase 4: Fonctionnalités Avancées
- [ ] Multi-langue (FR/AR)
- [ ] Support RTL
- [ ] Thème sombre/clair
- [ ] Raccourcis clavier
- [ ] Impression directe

---

## 🎯 Prochaines Étapes

1. **Installer PyQt5** ✅
2. **Tester l'interface de base** ⏳
3. **Créer l'interface caisse**
4. **Créer la gestion produits**
5. **Ajouter les autres modules**

---

**Status:** Interface de base créée ✅  
**Prochaine priorité:** Interface caisse (POS)
