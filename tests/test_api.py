import os
import tempfile
import uuid
import json
import shutil

import pytest
from fastapi.testclient import TestClient


def setup_test_env(tmp_path):
    db_file = tmp_path / "test_cars.db"
    os.environ["DATABASE_URL"] = str(db_file)
    os.environ["API_KEY"] = "testkey"
    return str(db_file)


def test_api_crud(tmp_path):
    db_path = setup_test_env(tmp_path)

    # import app after env is set
    from main import app
    from app.db import init_db

    init_db()
    client = TestClient(app)

    # unauthorized
    r = client.get("/api/cars")
    assert r.status_code == 401

    headers = {"X-API-Key": "testkey"}

    # create brand
    r = client.post("/api/brands", json={"name": "TestBrand"}, headers=headers)
    assert r.status_code == 200
    brand = r.json()
    assert "id" in brand

    # list brands
    r = client.get("/api/brands", headers=headers)
    assert r.status_code == 200
    assert any(b["name"] == "TestBrand" for b in r.json())

    # create model
    r = client.post("/api/models", json={"brand_id": brand["id"], "name": "ModelX", "year": 2023}, headers=headers)
    assert r.status_code == 200
    model = r.json()

    # create car
    car_payload = {"model_id": model["id"], "vin": "TESTVIN123", "color": "Blue", "price": 19999.0, "status": "available"}
    r = client.post("/api/cars", json=car_payload, headers=headers)
    assert r.status_code == 200
    car = r.json()
    car_id = car["id"]

    # get car
    r = client.get(f"/api/cars/{car_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["vin"] == "TESTVIN123"

    # update car
    updated = {"model_id": model["id"], "vin": "TESTVIN123", "color": "Red", "price": 18999.0, "status": "available"}
    r = client.put(f"/api/cars/{car_id}", json=updated, headers=headers)
    assert r.status_code == 200
    assert r.json()["color"] == "Red"

    # delete car
    r = client.delete(f"/api/cars/{car_id}", headers=headers)
    assert r.status_code == 200

    # ensure deleted
    r = client.get(f"/api/cars/{car_id}", headers=headers)
    assert r.status_code == 404
