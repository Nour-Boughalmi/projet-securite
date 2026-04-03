from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_sans_credentials():
    """Route protégée doit retourner 401 sans token"""
    response = client.get("/dashboard")
    assert response.status_code in [401, 403]

def test_login_mauvais_mdp():
    """Brute force doit être détecté ou refusé"""
    response = client.post("/login", json={
        "username": "admin",
        "password": "mauvais_mdp"
    })
    assert response.status_code in [401, 422]

def test_detection_brute_force():
    """Simuler plusieurs tentatives échouées"""
    from app.detection import detecter_brute_force
    # adapte selon ta fonction réelle
    result = detecter_brute_force(tentatives=10, fenetre_minutes=5)
    assert result == True