from fastapi.testclient import TestClient
from src.web_server import app

client = TestClient(app)

def test_health_check():
    """Verify that the FastAPI root page responds with 200 OK."""
    response = client.get("/")
    assert response.status_code == 200

def test_eval_history_endpoint():
    """Verify eval history API returns a valid list."""
    response = client.get("/evals/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
