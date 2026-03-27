from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

SECRET_KEY = os.getenv("SECRET_KEY", "changez_cette_cle_en_production_svp")
ALGORITHME = "HS256"


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    mot_de_passe = mot_de_passe[:72]  # Limite bcrypt
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    mot_de_passe = mot_de_passe[:72]  # Limite bcrypt
    return pwd_context.verify(mot_de_passe, hash)


def creer_token(username: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(
        {"sub": username, "exp": expiration},
        SECRET_KEY,
        algorithm=ALGORITHME,
    )