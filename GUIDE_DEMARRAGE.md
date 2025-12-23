# Guide de Démarrage Rapide - Gestion Mini-Market

## 🚀 Installation et Premier Lancement

### 1. Vérifier Python

```bash
python --version
# Doit être Python 3.8 ou supérieur
```

### 2. Installer les dépendances

```bash
cd "c:\Users\msi\Desktop\gestion de stock"
pip install -r requirements.txt
```

**Dépendances principales:**
- `bcrypt` - Sécurité des mots de passe
- `reportlab` - Génération PDF
- `openpyxl` - Import/Export Excel
- `python-dateutil` - Gestion des dates
- `pillow` - Traitement d'images

### 3. Lancer l'application

```bash
python main.py
```

**Résultat attendu:**
```
✓ Base de données initialisée avec succès
✓ Application initialisée avec succès
```

### 4. Tester les modules

```bash
python test_modules.py
```

**Tests effectués:**
- ✅ Authentification
- ✅ Catégories
- ✅ Produits
- ✅ Clients
- ✅ Point de vente
- ✅ Rapports

---

## 🔑 Connexion par Défaut

**Compte administrateur:**
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Changez ce mot de passe après la première connexion !

---

## 📚 Utilisation des Modules

### Créer un Produit

```python
from modules.products.product_manager import product_manager

success, message, product_id = product_manager.create_product(
    name="Lait Candia 1L",
    name_ar="حليب كانديا 1 لتر",
    selling_price=120.0,
    purchase_price=90.0,
    barcode="6111000123456",
    category_id=1,  # Alimentation
    stock_quantity=100,
    min_stock_level=20,
    created_by=1
)

if success:
    print(f"✓ Produit créé avec ID: {product_id}")
```

### Effectuer une Vente

```python
from modules.sales.pos import pos_manager

# Nouvelle vente
pos_manager.new_sale()

# Ajouter des produits
pos_manager.add_product_by_barcode("6111000123456", quantity=3)

# Appliquer une réduction de 10%
cart = pos_manager.get_cart()
cart.set_discount_percentage(10)

# Finaliser
success, message, sale_id = pos_manager.complete_sale(
    cashier_id=1,
    payment_method='cash',
    amount_paid=400.0
)

print(f"✓ Vente enregistrée: {message}")
```

### Créer un Client

```python
from modules.customers.customer_manager import customer_manager

success, message, customer_id = customer_manager.create_customer(
    full_name="Mohamed Alami",
    phone="0661234567",
    credit_limit=10000.0
)

print(f"✓ {message}")
```

### Générer un Rapport

```python
from modules.reports.sales_report import sales_report_manager
from datetime import datetime

# Ventes du jour
today = datetime.now().strftime('%Y-%m-%d')
stats = sales_report_manager.get_daily_sales(today)

print(f"Nombre de ventes: {stats['sale_count']}")
print(f"Chiffre d'affaires: {stats['total_revenue']} DA")
print(f"Vente moyenne: {stats['average_sale']} DA")
```

### Sauvegarder la Base de Données

```python
from core.backup import backup_manager

# Sauvegarde manuelle
success, message, path = backup_manager.create_backup()
print(f"✓ {message}")

# Export vers clé USB
from pathlib import Path
success, message = backup_manager.export_to_usb(Path("E:/"))
```

---

## 📁 Structure des Fichiers

```
gestion de stock/
├── main.py                 # ← Lancer l'application
├── test_modules.py         # ← Tester les modules
├── config.py               # Configuration
├── requirements.txt        # Dépendances
├── README.md              # Documentation
│
├── database/              # Base de données
│   ├── schema.sql         # Schéma SQLite
│   └── db_manager.py      # Gestionnaire
│
├── core/                  # Infrastructure
│   ├── auth.py           # Authentification
│   ├── logger.py         # Logs
│   ├── security.py       # Sécurité
│   └── backup.py         # Sauvegarde
│
├── modules/              # Modules métier
│   ├── products/        # Produits & stock
│   ├── sales/           # Ventes & caisse
│   ├── customers/       # Clients
│   ├── suppliers/       # Fournisseurs
│   └── reports/         # Rapports
│
├── data/                # Données (généré)
│   ├── minimarket.db   # Base SQLite
│   ├── backups/        # Sauvegardes
│   └── receipts/       # Tickets PDF
│
└── logs/               # Journaux
    └── app.log        # Fichier de log
```

---

## 🛠️ Commandes Utiles

### Vérifier la base de données

```python
from database.db_manager import db

info = db.get_database_info()
print(f"Tables: {info['tables']}")
print(f"Taille: {info['size_bytes'] / 1024:.2f} KB")

for table, count in info['table_counts'].items():
    print(f"  {table}: {count} enregistrements")
```

### Lister les produits en stock faible

```python
from modules.products.product_manager import product_manager

low_stock = product_manager.get_low_stock_products()
for product in low_stock:
    print(f"⚠️ {product['name']}: {product['stock_quantity']} unités")
```

### Lister les clients avec crédit

```python
from modules.customers.customer_manager import customer_manager

customers = customer_manager.get_customers_with_credit()
for customer in customers:
    print(f"{customer['full_name']}: {customer['current_credit']} DA")
```

### Voir les ventes du jour

```python
from modules.reports.sales_report import sales_report_manager
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
sales = sales_report_manager.get_sales_by_period(today, today)

for sale in sales:
    print(f"Vente #{sale['sale_number']}: {sale['total_amount']} DA")
```

---

## ⚙️ Configuration

Modifier `config.py` pour personnaliser:

```python
# Informations du magasin
STORE_CONFIG = {
    "name": "Votre Mini-Market",
    "address": "123 Rue Principale",
    "phone": "+213 XX XX XX XX",
    "currency": "DA",
    "tax_rate": 19.0,  # TVA 19%
}

# Paramètres de stock
STOCK_CONFIG = {
    "low_stock_threshold": 10,
    "alert_expiry_days": 30,
    "auto_decrease_stock": True,
}

# Paramètres d'impression
PRINTER_CONFIG = {
    "default_printer": "PDF",  # "PDF", "THERMAL", "STANDARD"
    "paper_width_mm": 80,
    "auto_print": False,
}
```

---

## 🐛 Dépannage

### Erreur: Module 'bcrypt' introuvable

```bash
pip install bcrypt
```

### Erreur: Base de données verrouillée

La base SQLite ne supporte qu'un seul processus d'écriture à la fois.
Fermez toutes les instances de l'application.

### Erreur: Permission refusée sur data/

Vérifiez les permissions du dossier:
```bash
# Windows
icacls "data" /grant Users:F
```

### Les logs ne s'affichent pas

Vérifiez le niveau de log dans `config.py`:
```python
LOG_CONFIG = {
    "log_level": "INFO",  # Changez en "DEBUG" pour plus de détails
}
```

---

## 📞 Support

Pour toute question ou problème:

1. Consultez le `README.md`
2. Vérifiez les logs dans `logs/app.log`
3. Testez avec `python test_modules.py`

---

## 🎯 Prochaines Étapes

1. **Interface PyQt5** - Créer l'interface graphique
2. **Multi-langue** - Ajouter support arabe (RTL)
3. **Import/Export Excel** - Gestion en masse
4. **Compilation .exe** - Créer l'exécutable

---

**Version:** 1.0.0  
**Date:** Décembre 2025  
**Statut:** Backend opérationnel ✅
