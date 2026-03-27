from app.database import db, sauvegarder_alerte
from datetime import datetime, timedelta


async def analyser_logs():
    """Appelée automatiquement toutes les 60 secondes"""
    print(f"🔍 Analyse des logs... ({datetime.now().strftime('%H:%M:%S')})")
    await regle_brute_force()
    await regle_compte_inexistant()
    await regle_volume_anormal()
    await regle_scan_pages()
    print("✅ Analyse terminée.")


async def regle_brute_force():
    """RÈGLE 1 : 5+ échecs depuis la même IP en 10 minutes → BRUTE_FORCE (HIGH)"""
    depuis = datetime.now() - timedelta(minutes=10)
    pipeline = [
        {"$match": {"event": "LOGIN_FAILED", "timestamp": {"$gte": depuis}}},
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 5}}},
    ]
    async for result in db.logs.aggregate(pipeline):
        ip = result["_id"]
        existe = await db.alertes.find_one({
            "type": "BRUTE_FORCE", "ip": ip,
            "timestamp": {"$gte": depuis},
        })
        if not existe:
            await sauvegarder_alerte("BRUTE_FORCE", ip, "inconnu", "HIGH")
            print(f"🚨 BRUTE FORCE détecté depuis {ip}")


async def regle_compte_inexistant():
    """RÈGLE 2 : 3+ tentatives sur un compte inexistant → ENUMERATION_COMPTES (MEDIUM)"""
    depuis = datetime.now() - timedelta(minutes=10)
    utilisateurs_valides = ["admin", "alice"]
    pipeline = [
        {
            "$match": {
                "event": "LOGIN_FAILED",
                "timestamp": {"$gte": depuis},
                "username": {"$nin": utilisateurs_valides},
            }
        },
        {"$group": {"_id": "$username", "count": {"$sum": 1}, "ip": {"$last": "$ip"}}},
        {"$match": {"count": {"$gte": 3}}},
    ]
    async for result in db.logs.aggregate(pipeline):
        username = result["_id"]
        ip = result["ip"]
        existe = await db.alertes.find_one({
            "type": "ENUMERATION_COMPTES", "username": username,
            "timestamp": {"$gte": depuis},
        })
        if not existe:
            await sauvegarder_alerte("ENUMERATION_COMPTES", ip, username, "MEDIUM")
            print(f"⚠️ Énumération : '{username}' depuis {ip}")


async def regle_volume_anormal():
    """RÈGLE 3 : 20+ requêtes en 5 minutes → VOLUME_ANORMAL (MEDIUM)"""
    depuis = datetime.now() - timedelta(minutes=5)
    pipeline = [
        {"$match": {"timestamp": {"$gte": depuis}}},
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 20}}},
    ]
    async for result in db.logs.aggregate(pipeline):
        ip = result["_id"]
        existe = await db.alertes.find_one({
            "type": "VOLUME_ANORMAL", "ip": ip,
            "timestamp": {"$gte": depuis},
        })
        if not existe:
            await sauvegarder_alerte("VOLUME_ANORMAL", ip, "inconnu", "MEDIUM")
            print(f"⚠️ Volume anormal depuis {ip}")


async def regle_scan_pages():
    """RÈGLE 4 : 10+ erreurs 404 depuis la même IP → SCAN_VULNERABILITES (MEDIUM)"""
    depuis = datetime.now() - timedelta(minutes=5)
    pipeline = [
        {"$match": {"type": "ERROR", "error_code": 404, "timestamp": {"$gte": depuis}}},
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 10}}},
    ]
    async for result in db.logs.aggregate(pipeline):
        ip = result["_id"]
        existe = await db.alertes.find_one({
            "type": "SCAN_VULNERABILITES", "ip": ip,
            "timestamp": {"$gte": depuis},
        })
        if not existe:
            await sauvegarder_alerte("SCAN_VULNERABILITES", ip, "inconnu", "MEDIUM")
            print(f"⚠️ Scan de vulnérabilités depuis {ip}")
