from main import app
from fastapi.testclient import TestClient


def test_scrape_endpoint():
    client = TestClient(app)
    headers = {"X-API-Key": "testkey"}

    html = """
    <div class="listing" data-vin="VIN123">
      <div class="title">Falcon</div>
      <div class="price">$12,345</div>
      <div class="color">Blue</div>
    </div>
    <div class="listing">
      <div class="title">Orion</div>
      <div class="price">$9,999</div>
    </div>
    """

    # ensure env API_KEY is set in CI/test env; if not, tests may fail with 401
    r = client.post("/api/scrape", headers=headers, json={"html": html})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert isinstance(data["results"], list)
