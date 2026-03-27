# 🔒 Application Web Sécurisée — Détection d'Intrusions

> Déploiement cloud avec supervision et détection d'activités suspectes en temps réel

## 🚀 Demo en ligne
**URL :** `https://projet-securite.onrender.com`

---

## 🛠️ Technologies

| Technologie | Rôle |
|------------|------|
| **FastAPI** (Python) | API REST + backend |
| **MongoDB Atlas** | Logs et alertes |
| **Render.com** | Déploiement cloud HTTPS |
| **Bootstrap 5** | Interface utilisateur |
| **bcrypt** | Hachage des mots de passe |

---

## 🔐 Fonctionnalités

- ✅ Login sécurisé avec mots de passe **hachés bcrypt**
- ✅ **HTTPS** automatique
- ✅ 3 types de logs : **AUTH**, **NETWORK**, **ERROR**
- ✅ **5 règles de détection** automatique

### Règles de détection
| Règle | Condition | Sévérité |
|-------|-----------|----------|
| 🔨 Brute Force | ≥ 5 échecs / IP en 10 min | HIGH |
| 🌙 Connexion nocturne | Entre 00h et 05h | MEDIUM |
| 🔍 Énumération comptes | ≥ 3 essais compte inexistant | MEDIUM |
| ⚠️ Volume anormal | ≥ 20 requêtes en 5 min | MEDIUM |
| 🕵️ Scan vulnérabilités | ≥ 10 erreurs 404 en 5 min | MEDIUM |

---

## 💻 Lancer localement

```bash
pip install -r requirements.txt
cp .env.example .env
# Remplis .env avec tes identifiants MongoDB
uvicorn app.main:app --reload
```

Ouvre `http://localhost:8000`

---

## 🧪 Simuler des attaques

```bash
python simulate_attack.py
```

Puis va sur `/alertes` pour voir les alertes générées.

---

## 🧪 Comptes de test

| Utilisateur | Mot de passe |
|------------|-------------|
| `admin` | `admin123` |
| `alice` | `alice456` |
