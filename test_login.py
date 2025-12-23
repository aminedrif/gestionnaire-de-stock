# -*- coding: utf-8 -*-
"""
Script pour tester la connexion admin
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.auth import auth_manager

print("Test de connexion...")
print("Username: admin")
print("Password: admin123")
print()

success, message, user_data = auth_manager.login("admin", "admin123")

if success:
    print("✓ CONNEXION RÉUSSIE!")
    print(f"  Utilisateur: {user_data['username']}")
    print(f"  Nom: {user_data['full_name']}")
    print(f"  Rôle: {user_data['role']}")
else:
    print(f"✗ ÉCHEC DE CONNEXION")
    print(f"  Message: {message}")
