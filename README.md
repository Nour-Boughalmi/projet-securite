# Secure Web Application — Intrusion Detection System

> Pipeline CI/CD sécurisé avec supervision applicative et détection d'anomalies en temps réel.  

![Security CI](https://github.com/Nour-Boughalmi/projet-securite/actions/workflows/security-ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-secured-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

**Live demo :** `https://projet-securite.onrender.com`

---

## Contexte du projet

Ce projet implémente une application web sécurisée avec un **pipeline CI/CD intégrant des contrôles de sécurité automatisés** à chaque étape (approche shift-left). Il démontre la mise en œuvre concrète des pratiques DevSecOps : sécurisation du code, analyse statique, tests automatisés et déploiement conditionnel.

---

## Pipeline CI/CD — GitHub Actions

Le déploiement est conditionné au succès de 3 étapes de sécurité séquentielles :

```
git push
    │
    ├─ 1. SAST (Bandit)       — scan statique des vulnérabilités Python
    ├─ 2. SCA  (Safety)       — analyse des dépendances / CVE
    ├─ 3. Tests (pytest)      — couverture de code + tests sécurité
    │
    ├─ 4. Docker build        — containerisation et validation image
    │
    └─ 5. Deploy (Render)     — déploiement uniquement si tout est vert
```

**Principe appliqué :** le déploiement est bloqué automatiquement si une vulnérabilité critique est détectée — sans intervention manuelle.

---

## Stack technique

| Composant | Technologie | Rôle DevSecOps |
|---|---|---|
| API REST | FastAPI (Python 3.11) | Backend sécurisé, contrôle d'accès |
| Authentification | JWT + bcrypt | Gestion des rôles, hachage des mots de passe |
| Supervision des logs | MongoDB Atlas | Collecte et analyse des événements de sécurité |
| Dashboard | Interface web (Bootstrap 5) | Visualisation temps réel des alertes |
| Containerisation | Docker | Environnement reproductible, déploiement cohérent |
| CI/CD | GitHub Actions | Pipeline automatisé avec gates de sécurité |
| Déploiement cloud | Render.com (HTTPS) | Déploiement conditionnel, infrastructure as code |
| Analyse statique | Bandit | SAST — détection de vulnérabilités dans le code |
| Analyse dépendances | Safety | SCA — vérification des CVE dans les bibliothèques |

---

## Fonctionnalités de sécurité

### Contrôle d'accès
- Authentification JWT avec gestion des rôles (admin / utilisateur)
- Mots de passe hachés bcrypt — aucun stockage en clair
- HTTPS automatique via Render

### Supervision et détection d'anomalies

5 règles de détection implémentées sur 3 types de logs (AUTH, NETWORK, ERROR) :

| Règle | Condition de déclenchement | Sévérité | KPI associé |
|---|---|---|---|
| Brute force | ≥ 5 échecs / IP en 10 min | HIGH | Taux d'authentification échouée |
| Connexion hors horaire | Entre 00h et 05h | MEDIUM | Anomalies temporelles |
| Énumération de comptes | ≥ 3 essais sur compte inexistant | MEDIUM | Taux d'erreurs 401 |
| Volume anormal de requêtes | ≥ 20 req. en 5 min | MEDIUM | Throughput applicatif |
| Scan de vulnérabilités | ≥ 10 erreurs 404 en 5 min | MEDIUM | Taux d'erreurs 4xx |

### Métriques de supervision (KPIs)
- Taux de succès / échec des authentifications
- Volume de requêtes par fenêtre temporelle
- Nombre d'alertes actives par sévérité
- Taux de détection sur attaques simulées

---

## Lancer le projet

### Avec Docker (recommandé)

```bash
docker build -t secure-app .
docker run -p 8000:8000 --env-file .env secure-app
```

### En local

```bash
pip install -r requirements.txt
cp .env.example .env
# Configurer les variables MongoDB dans .env
uvicorn app.main:app --reload
```

Accès : `http://localhost:8000`

---

## Tests

```bash
# Tests unitaires + rapport de couverture
pytest tests/ -v --cov=app --cov-report=term-missing

# Simulation d'attaques pour valider la détection
python simulate_attack.py
```

Les résultats de couverture sont générés automatiquement dans le pipeline CI à chaque push.

---

## Structure du projet

```
├── app/
│   ├── main.py          # Entrée API, routing, middlewares
│   ├── securite.py      # Auth JWT, bcrypt, contrôle d'accès
│   ├── detection.py     # Moteur de détection d'anomalies (5 règles)
│   ├── database.py      # Connexion MongoDB, modèles de logs
│   └── templates/       # Dashboards HTML (supervision, alertes, logs)
├── tests/               # Tests unitaires sécurité + détection
├── .github/workflows/   # Pipeline CI/CD GitHub Actions
├── Dockerfile           # Containerisation reproductible
├── render.yaml          # Infrastructure as code — déploiement Render
├── simulate_attack.py   # Générateur de scénarios d'attaque
└── requirements.txt
```

---

## Lien avec les pratiques DevSecOps

Ce projet illustre concrètement plusieurs principes DevSecOps applicables en environnement industriel :

- **Shift-left security** : les contrôles de sécurité (SAST, SCA, tests) sont intégrés en amont du déploiement
- **Infrastructure as code** : déploiement Render entièrement déclaratif via `render.yaml`
- **Pipeline conditionnel** : déploiement bloqué automatiquement si les gates de sécurité échouent
- **Supervision continue** : logs structurés, alertes en temps réel, dashboard de supervision
- **Traçabilité** : chaque run CI génère un rapport de scan archivé (artifact GitHub)
