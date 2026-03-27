"""
simulate_attack.py
──────────────────
Script de simulation d'attaques sur TON application.
Lance uniquement contre localhost ou ton URL Render personnelle.

Usage :
    python simulate_attack.py
"""

import requests
import time

# ── Change cette URL selon où tourne ton app ─────────────────────────────────
BASE_URL = "http://localhost:8000"
# BASE_URL = "https://ton-app.onrender.com"  # ← décommente pour tester en ligne


def attaque_brute_force():
    """Simule une attaque brute force : 6 tentatives avec mauvais mots de passe"""
    print("\n🔴 ATTAQUE 1 — Brute Force")
    print("─" * 40)

    mots_de_passe = ["123456", "password", "admin", "azerty", "bonjour", "hacker"]

    for mdp in mots_de_passe:
        response = requests.post(f"{BASE_URL}/login", data={
            "username": "admin",
            "password": mdp
        })
        print(f"  Essai '{mdp}' → HTTP {response.status_code}")
        time.sleep(0.5)  # Petite pause entre chaque essai

    print("✅ Brute force terminé → vérifie /alertes pour BRUTE_FORCE")


def attaque_enumeration():
    """Simule une énumération de comptes : essaie des usernames inexistants"""
    print("\n🔴 ATTAQUE 2 — Énumération de comptes")
    print("─" * 40)

    usernames_inexistants = ["root", "superadmin", "sarah", "mohammed", "guest"]

    for username in usernames_inexistants:
        response = requests.post(f"{BASE_URL}/login", data={
            "username": username,
            "password": "faux_mot_de_passe"
        })
        print(f"  Essai username '{username}' → HTTP {response.status_code}")
        time.sleep(0.5)

    print("✅ Énumération terminée → vérifie /alertes pour ENUMERATION_COMPTES")


def attaque_scan_pages():
    """Simule un scan de vulnérabilités : accède à des pages qui n'existent pas"""
    print("\n🔴 ATTAQUE 3 — Scan de pages sensibles")
    print("─" * 40)

    pages_sensibles = [
        "/admin", "/admin/config", "/config", "/secret",
        "/.env", "/backup", "/api/users", "/root",
        "/phpinfo", "/wp-admin"
    ]

    for page in pages_sensibles:
        response = requests.get(f"{BASE_URL}{page}")
        print(f"  Accès {page} → HTTP {response.status_code}")
        time.sleep(0.3)

    print("✅ Scan terminé → vérifie /alertes pour SCAN_VULNERABILITES")


def attaque_volume():
    """Simule un volume anormal de requêtes : 25 requêtes rapides"""
    print("\n🔴 ATTAQUE 4 — Volume anormal de requêtes")
    print("─" * 40)

    for i in range(25):
        requests.get(f"{BASE_URL}/ping")
        print(f"  Requête {i+1}/25 envoyée")

    print("✅ Volume anormal terminé → vérifie /alertes pour VOLUME_ANORMAL")


if __name__ == "__main__":
    print("=" * 50)
    print("🎯 SIMULATION D'ATTAQUES — Application Sécurisée")
    print(f"   Cible : {BASE_URL}")
    print("=" * 50)

    attaque_brute_force()
    time.sleep(2)

    attaque_enumeration()
    time.sleep(2)

    attaque_scan_pages()
    time.sleep(2)

    attaque_volume()

    print("\n" + "=" * 50)
    print("🏁 Toutes les attaques terminées !")
    print(f"   Ouvre {BASE_URL}/alertes pour voir les alertes")
    print(f"   Ouvre {BASE_URL}/logs pour voir tous les logs")
    print("=" * 50)
