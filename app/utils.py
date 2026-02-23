from app import db
import uuid

def seed_data():
    conn = db.get_db()
    cur = conn.cursor()
    # sample brands
    brands = ["Acme Motors", "Nova Autos", "Silverline"]
    brand_ids = []
    for b in brands:
        bid = uuid.uuid4().hex
        try:
            cur.execute("INSERT INTO brands (id, name) VALUES (?,?)", (bid, b))
            brand_ids.append(bid)
        except:
            # skip if exists
            cur.execute("SELECT id FROM brands WHERE name=?", (b,))
            row = cur.fetchone()
            if row:
                brand_ids.append(row[0])

    # sample models
    models = [
        (brand_ids[0], "Falcon", 2021),
        (brand_ids[1], "Orion", 2022),
        (brand_ids[2], "Mercury", 2020),
    ]
    model_ids = []
    for br_id, name, year in models:
        mid = uuid.uuid4().hex
        try:
            cur.execute("INSERT INTO car_models (id, brand_id, name, year) VALUES (?,?,?,?)", (mid, br_id, name, year))
            model_ids.append(mid)
        except:
            cur.execute("SELECT id FROM car_models WHERE name=? AND brand_id=?", (name, br_id))
            row = cur.fetchone()
            if row:
                model_ids.append(row[0])

    # sample cars
    cars = [
        (model_ids[0], "1HGBH41JXMN109186", "Navy", 25000.0, "available"),
        (model_ids[1], "2HGCM82633A004352", "Silver", 30000.0, "available"),
        (model_ids[2], "3FAHP0HA6AR123456", "Black", 18000.0, "sold"),
    ]
    for m_id, vin, color, price, status in cars:
        cid = uuid.uuid4().hex
        try:
            cur.execute("INSERT INTO cars (id, model_id, vin, color, price, status) VALUES (?,?,?,?,?,?)",
                        (cid, m_id, vin, color, price, status))
        except:
            continue

    conn.commit()
    conn.close()
