from fastapi import APIRouter, Depends, HTTPException
from app import db
from app import schemas
from app.auth import get_api_key
import uuid
from app.services import scraper

router = APIRouter(prefix="/api", tags=["cars"])


# Brands
@router.post("/brands", response_model=schemas.Brand, dependencies=[Depends(get_api_key)])
def create_brand(payload: schemas.BrandBase):
    conn = db.get_db()
    cur = conn.cursor()
    id_ = uuid.uuid4().hex
    try:
        cur.execute("INSERT INTO brands (id, name) VALUES (?,?)", (id_, payload.name))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    cur.execute("SELECT id, name FROM brands WHERE id=?", (id_,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "name": row[1]}


@router.get("/brands", response_model=list[schemas.Brand], dependencies=[Depends(get_api_key)])
def list_brands():
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM brands")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]


# Car models
@router.post("/models", response_model=schemas.CarModel, dependencies=[Depends(get_api_key)])
def create_model(payload: schemas.CarModelBase):
    conn = db.get_db()
    cur = conn.cursor()
    id_ = uuid.uuid4().hex
    try:
        cur.execute("INSERT INTO car_models (id, brand_id, name, year) VALUES (?,?,?,?)",
                    (id_, payload.brand_id, payload.name, payload.year))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    cur.execute("SELECT id, brand_id, name, year FROM car_models WHERE id=?", (id_,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "brand_id": row[1], "name": row[2], "year": row[3]}


@router.get("/models", response_model=list[schemas.CarModel], dependencies=[Depends(get_api_key)])
def list_models():
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, brand_id, name, year FROM car_models")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "brand_id": r[1], "name": r[2], "year": r[3]} for r in rows]


# Cars
@router.post("/cars", response_model=schemas.Car, dependencies=[Depends(get_api_key)])
def create_car(payload: schemas.CarBase):
    conn = db.get_db()
    cur = conn.cursor()
    id_ = uuid.uuid4().hex
    try:
        cur.execute(
            "INSERT INTO cars (id, model_id, vin, color, price, status) VALUES (?,?,?,?,?,?)",
            (id_, payload.model_id, payload.vin, payload.color, payload.price, payload.status)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    cur.execute("SELECT id, model_id, vin, color, price, status FROM cars WHERE id=?", (id_,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "model_id": row[1], "vin": row[2], "color": row[3], "price": row[4], "status": row[5]}


@router.get("/cars", response_model=list[schemas.Car], dependencies=[Depends(get_api_key)])
def list_cars():
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, model_id, vin, color, price, status FROM cars")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "model_id": r[1], "vin": r[2], "color": r[3], "price": r[4], "status": r[5]} for r in rows]


@router.get("/cars/{car_id}", response_model=schemas.Car, dependencies=[Depends(get_api_key)])
def get_car(car_id: str):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, model_id, vin, color, price, status FROM cars WHERE id=?", (car_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"id": row[0], "model_id": row[1], "vin": row[2], "color": row[3], "price": row[4], "status": row[5]}


@router.post("/scrape", dependencies=[Depends(get_api_key)])
def scrape_html(payload: dict):
    """Accepts JSON with `html` key and returns parsed listings using BeautifulSoup helper."""
    html = payload.get("html")
    if not html:
        raise HTTPException(status_code=400, detail="Missing 'html' in payload")
    try:
        results = scraper.parse_car_listings(html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"count": len(results), "results": results}


# Update and delete endpoints
@router.put("/cars/{car_id}", response_model=schemas.Car, dependencies=[Depends(get_api_key)])
def update_car(car_id: str, payload: schemas.CarBase):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cars SET model_id=?, vin=?, color=?, price=?, status=? WHERE id=?",
        (payload.model_id, payload.vin, payload.color, payload.price, payload.status, car_id),
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Car not found")
    conn.commit()
    cur.execute("SELECT id, model_id, vin, color, price, status FROM cars WHERE id=?", (car_id,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "model_id": row[1], "vin": row[2], "color": row[3], "price": row[4], "status": row[5]}


@router.delete("/cars/{car_id}", dependencies=[Depends(get_api_key)])
def delete_car(car_id: str):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM cars WHERE id=?", (car_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Car not found")
    conn.commit()
    conn.close()
    return {"detail": "deleted"}


# Brands update/delete
@router.put("/brands/{brand_id}", response_model=schemas.Brand, dependencies=[Depends(get_api_key)])
def update_brand(brand_id: str, payload: schemas.BrandBase):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("UPDATE brands SET name=? WHERE id=?", (payload.name, brand_id))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Brand not found")
    conn.commit()
    cur.execute("SELECT id, name FROM brands WHERE id=?", (brand_id,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "name": row[1]}


@router.delete("/brands/{brand_id}", dependencies=[Depends(get_api_key)])
def delete_brand(brand_id: str):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM brands WHERE id=?", (brand_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Brand not found")
    conn.commit()
    conn.close()
    return {"detail": "deleted"}


# Models update/delete
@router.put("/models/{model_id}", response_model=schemas.CarModel, dependencies=[Depends(get_api_key)])
def update_model(model_id: str, payload: schemas.CarModelBase):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("UPDATE car_models SET brand_id=?, name=?, year=? WHERE id=?",
                (payload.brand_id, payload.name, payload.year, model_id))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Model not found")
    conn.commit()
    cur.execute("SELECT id, brand_id, name, year FROM car_models WHERE id=?", (model_id,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "brand_id": row[1], "name": row[2], "year": row[3]}


@router.delete("/models/{model_id}", dependencies=[Depends(get_api_key)])
def delete_model(model_id: str):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM car_models WHERE id=?", (model_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Model not found")
    conn.commit()
    conn.close()
    return {"detail": "deleted"}
