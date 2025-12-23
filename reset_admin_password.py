# -*- coding: utf-8 -*-
"""
Script FINAL pour réinitialiser le mot de passe admin
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import db
from core.security import hash_password, verify_password

print("=== RÉINITIALISATION MOT DE PASSE ADMIN ===\n")

# Nouveau mot de passe
password = "admin123"

# Générer le hash
new_hash = hash_password(password)
print(f"✓ Hash généré: {new_hash[:60]}...")

# Mettre à jour dans la base de données avec execute_update (pas execute_query!)
rows_affected = db.execute_update("""
    UPDATE users 
    SET password_hash = ?,
        failed_login_attempts = 0,
        locked_until = NULL
    WHERE username = 'admin'
""", (new_hash,))

print(f"✓ {rows_affected} ligne(s) mise(s) à jour")

# Vérifier
user = db.fetch_one("SELECT username, password_hash FROM users WHERE username = 'admin'")
if user:
    print(f"✓ Utilisateur trouvé: {user['username']}")
    print(f"  Hash: {user['password_hash'][:60]}...")
    
    # Tester le mot de passe
    if verify_password(password, user['password_hash']):
        print(f"✓ TEST RÉUSSI - Le mot de passe fonctionne!")
        print(f"\n{'='*50}")
        print(f"  Username: admin")
        print(f"  Password: {password}")
        print(f"{'='*50}\n")
    else:
        print(f"✗ ERREUR - Le mot de passe ne fonctionne pas!")
else:
    print("✗ ERREUR - Utilisateur admin non trouvé!")
