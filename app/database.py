from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Charge le .env explicitement avec le chemin absolu
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
print(f"🔗 Connexion MongoDB : {MONGODB_URL[:30]}...")  # Affiche les 30 premiers caractères

client = AsyncIOMotorClient(MONGODB_URL)
db = client.securite_app

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.securite_app


async def sauvegarder_log(event: str, username: str, ip: str, succes: bool):
    """Enregistre chaque tentative de connexion dans MongoDB"""
    await db.logs.insert_one({
        "timestamp": datetime.now(),
        "type": "AUTH",
        "event": event,
        "username": username,
        "ip": ip,
        "succes": succes,
    })


async def sauvegarder_log_reseau(method: str, endpoint: str, ip: str, status_code: int):
    """Enregistre chaque requête HTTP"""
    await db.logs.insert_one({
        "timestamp": datetime.now(),
        "type": "NETWORK",
        "method": method,
        "endpoint": endpoint,
        "ip": ip,
        "status_code": status_code,
    })


async def sauvegarder_log_erreur(error_code: int, endpoint: str, ip: str):
    """Enregistre chaque erreur"""
    await db.logs.insert_one({
        "timestamp": datetime.now(),
        "type": "ERROR",
        "error_code": error_code,
        "endpoint": endpoint,
        "ip": ip,
    })


async def compter_echecs_recents(ip: str, minutes: int = 10) -> int:
    """Compte les échecs de login depuis une IP dans les X dernières minutes"""
    depuis = datetime.now() - timedelta(minutes=minutes)
    return await db.logs.count_documents({
        "ip": ip,
        "event": "LOGIN_FAILED",
        "timestamp": {"$gte": depuis},
    })


async def sauvegarder_alerte(type_alerte: str, ip: str, username: str, severite: str):
    """Crée une alerte de sécurité dans MongoDB"""
    await db.alertes.insert_one({
        "timestamp": datetime.now(),
        "type": type_alerte,
        "ip": ip,
        "username": username,
        "severite": severite,
        "traitee": False,
    })
