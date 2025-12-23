# -*- coding: utf-8 -*-
"""
Script de diagnostic pour le problème de connexion
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import db
from core.security import hash_password, verify_password
import bcrypt

print("=== DIAGNOSTIC CONNEXION ADMIN ===\n")

# 1. Vérifier l'utilisateur dans la DB
user = db.fetch_one("SELECT * FROM users WHERE username = 'admin'")
if not user:
    print("✗ ERREUR: Utilisateur admin non trouvé!")
    sys.exit(1)

print("✓ Utilisateur admin trouvé")
print(f"  ID: {user['id']}")
print(f"  Username: {user['username']}")
print(f"  Full name: {user['full_name']}")
print(f"  Role: {user['role']}")
print(f"  Is active: {user['is_active']}")
print(f"  Failed attempts: {user['failed_login_attempts']}")
print(f"  Locked until: {user['locked_until']}")
print(f"  Password hash: {user['password_hash'][:60]}...")
print()

# 2. Tester le hash actuel
password = "admin123"
print(f"Test du mot de passe: '{password}'")
print(f"Hash dans DB: {user['password_hash']}")
print()

# 3. Vérifier avec bcrypt directement
try:
    result = bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
    print(f"✓ Test bcrypt direct: {result}")
except Exception as e:
    print(f"✗ Erreur bcrypt: {e}")

# 4. Vérifier avec notre fonction
try:
    result = verify_password(password, user['password_hash'])
    print(f"✓ Test verify_password: {result}")
except Exception as e:
    print(f"✗ Erreur verify_password: {e}")

# 5. Créer un nouveau hash et le tester
print("\n=== CRÉATION D'UN NOUVEAU HASH ===")
new_hash = hash_password(password)
print(f"Nouveau hash: {new_hash}")
print(f"Test du nouveau hash: {verify_password(password, new_hash)}")

# 6. Mettre à jour la DB avec le nouveau hash
print("\n=== MISE À JOUR DE LA BASE DE DONNÉES ===")
db.execute_query(
    "UPDATE users SET password_hash = ?, failed_login_attempts = 0, locked_until = NULL WHERE username = 'admin'",
    (new_hash,)
)
print("✓ Hash mis à jour dans la base de données")

# 7. Vérifier à nouveau
user_updated = db.fetch_one("SELECT password_hash FROM users WHERE username = 'admin'")
print(f"Hash dans DB après update: {user_updated['password_hash'][:60]}...")
print(f"Test final: {verify_password(password, user_updated['password_hash'])}")

print("\n✓ DIAGNOSTIC TERMINÉ - Essayez de vous connecter maintenant!")
