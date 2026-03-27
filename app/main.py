from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from app.securite import hacher_mot_de_passe, verifier_mot_de_passe
from app.database import (
    db, sauvegarder_log, sauvegarder_log_reseau,
    sauvegarder_log_erreur, sauvegarder_alerte, compter_echecs_recents
)
from app.detection import analyser_logs



# ── Utilisateurs (mots de passe hachés) ──────────────────────────────────────
UTILISATEURS = {
    "admin": hacher_mot_de_passe("admin123"),
    "alice": hacher_mot_de_passe("alice456"),
}

# ── Scheduler : détection toutes les 60 secondes ─────────────────────────────
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(analyser_logs, "interval", seconds=60)
    scheduler.start()
    print("✅ Détection automatique démarrée (toutes les 60s)")
    yield
    scheduler.shutdown()

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="🔒 Application Sécurisée",
    description="Détection d'intrusions en temps réel",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

# ── Middleware : log chaque requête réseau ────────────────────────────────────
@app.middleware("http")
async def log_requetes(request: Request, call_next):
    response = await call_next(request)
    ip = request.client.host
    # Log toutes les requêtes sauf /docs et /openapi
    if not request.url.path.startswith("/docs") and \
       not request.url.path.startswith("/openapi"):
        await sauvegarder_log_reseau(
            request.method,
            request.url.path,
            ip,
            response.status_code
        )
        # Log erreur si 404 ou 500
        if response.status_code in [404, 500]:
            await sauvegarder_log_erreur(
                response.status_code,
                request.url.path,
                ip
            )
    return response

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/")
async def accueil(request: Request):
    return templates.TemplateResponse("accueil.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"status": "ok", "heure": datetime.now().isoformat()}


@app.get("/login")
async def page_login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request, "erreur": None
    })


@app.post("/login")
async def traiter_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    ip = request.client.host
    hash_stocke = UTILISATEURS.get(username)

    if not hash_stocke or not verifier_mot_de_passe(password, hash_stocke):
        await sauvegarder_log("LOGIN_FAILED", username, ip, succes=False)

        # Règle brute force immédiate
        nb_echecs = await compter_echecs_recents(ip, minutes=10)
        if nb_echecs >= 5:
            await sauvegarder_alerte("BRUTE_FORCE", ip, username, "HIGH")

        return templates.TemplateResponse("login.html", {
            "request": request,
            "erreur": "Nom d'utilisateur ou mot de passe incorrect"
        })

    await sauvegarder_log("LOGIN_SUCCESS", username, ip, succes=True)

    # Règle connexion nocturne
    heure = datetime.now().hour
    if 0 <= heure <= 5:
        await sauvegarder_alerte("CONNEXION_NOCTURNE", ip, username, "MEDIUM")

    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/dashboard")
async def dashboard(request: Request):
    total_logs = await db.logs.count_documents({})
    total_alertes = await db.alertes.count_documents({})
    echecs = await db.logs.count_documents({"event": "LOGIN_FAILED"})
    succes = await db.logs.count_documents({"event": "LOGIN_SUCCESS"})
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_logs": total_logs,
        "total_alertes": total_alertes,
        "echecs": echecs,
        "succes": succes,
    })


@app.get("/alertes")
async def page_alertes(request: Request):
    alertes = await db.alertes.find().sort("timestamp", -1).limit(50).to_list(50)
    for a in alertes:
        a["_id"] = str(a["_id"])
        a["timestamp"] = a["timestamp"].strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse("alertes.html", {
        "request": request, "alertes": alertes
    })


@app.get("/logs")
async def page_logs(request: Request):
    logs = await db.logs.find().sort("timestamp", -1).limit(100).to_list(100)
    for l in logs:
        l["_id"] = str(l["_id"])
        l["timestamp"] = l["timestamp"].strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse("logs.html", {
        "request": request, "logs": logs
    })


@app.get("/logout")
async def logout():
    return RedirectResponse(url="/", status_code=302)
