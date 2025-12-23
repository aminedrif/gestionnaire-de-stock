# -*- coding: utf-8 -*-
"""
Script pour débloquer le compte admin
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import db

# Débloquer le compte admin
db.execute_query("""
    UPDATE users 
    SET failed_login_attempts = 0,
        locked_until = NULL
    WHERE username = 'admin'
""")

print("✓ Compte admin débloqué avec succès!")
print("Vous pouvez maintenant vous connecter avec: admin / admin123")
