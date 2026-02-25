# -*- coding: utf-8 -*-
"""
Utilitaire de génération de clés de licence PERMANENTES
+ Génération de nom d'utilisateur et mot de passe par défaut
À utiliser par le développeur uniquement
"""
import hashlib
import string
import random


def generate_license_key(client_name: str, machine_id: str) -> str:
    """
    Générer une clé de licence PERMANENTE
    """
    secret = "AKHRIB_SUPERETTE_2024_SECRET"
    
    # Hash de validation basé UNIQUEMENT sur l'ID machine pour lock
    data_to_hash = f"{machine_id}_{secret}"
    validation_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()[:12].upper()
    
    return f"PRO-{validation_hash}"


def generate_default_credentials(client_name: str):
    """
    Générer un nom d'utilisateur et mot de passe par défaut pour un client.
    Le client pourra les changer après la première connexion.
    
    Returns:
        (username, password)
    """
    # Générer le username à partir du nom du client
    # Nettoyer le nom: enlever les espaces, accents, caractères spéciaux
    clean_name = client_name.strip().lower()
    clean_name = clean_name.replace(" ", "")
    # Garder uniquement les caractères alphanumériques
    clean_name = ''.join(c for c in clean_name if c.isalnum())
    
    if not clean_name:
        clean_name = "user"
    
    # Limiter à 15 caractères
    username = clean_name[:15]
    
    # Générer un mot de passe aléatoire de 8 caractères
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(8))
    
    return username, password


def main():
    print("=" * 60)
    print("🔑 GÉNÉRATEUR DE CLÉS DE LICENCE PRO (MACHINE LOCK)")
    print("DamDev POS")
    print("=" * 60)
    print()
    
    # Demander les informations
    client_name = input("Nom du client (pour référence): ").strip()
    
    print("\n⚠️  IMPORTANT: Vous devez obtenir l'ID Machine du client.")
    print("   L'ID s'affiche quand il lance le logiciel sans licence.")
    machine_id = input("ID Machine du client (ex: 1234-ABCD-5678-EF90): ").strip()
    
    if not machine_id:
        print("❌ L'ID Machine est obligatoire pour la sécurité !")
        return
    
    # Générer la clé
    license_key = generate_license_key(client_name, machine_id)
    
    # Générer les identifiants par défaut
    username, password = generate_default_credentials(client_name)
    
    print()
    print("=" * 60)
    print("✅ CLÉ SÉCURISÉE ET IDENTIFIANTS GÉNÉRÉS")
    print("=" * 60)
    print()
    print(f"Client: {client_name}")
    print(f"Machine ID: {machine_id}")
    print(f"Type: LICENCE À VIE (Verrouillée sur cette machine)")
    print()
    print(f"🔐 CLÉ: {license_key}")
    print()
    print("━" * 60)
    print("👤 IDENTIFIANTS PAR DÉFAUT")
    print("━" * 60)
    print(f"   Nom d'utilisateur: {username}")
    print(f"   Mot de passe:      {password}")
    print()
    print("⚠️  Le client peut changer ces identifiants après connexion")
    print("━" * 60)
    print()
    print("Instructions:")
    print("1. Envoyez la CLÉ, le NOM D'UTILISATEUR et le MOT DE PASSE au client.")
    print("2. La clé ne fonctionnera QUE sur sa machine.")
    print("3. S'il change de PC, il faudra une nouvelle clé.")
    print("4. Le client peut changer son mot de passe dans les paramètres.")
    print()
    print("📧 Contact: DamDev Solutions")
    print()
    input("Appuyez sur Entrée pour fermer...")


if __name__ == "__main__":
    main()
