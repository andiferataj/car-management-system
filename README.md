# Car Management System

This repository contains a simple Car Management System built with FastAPI, SQLite, Pydantic, and Streamlit.

Quick start

1. Copy `.env.example` to `.env` and set `API_KEY` and `DATABASE_URL`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the API:

```bash
uvicorn main:app --reload
```

4. Run the Streamlit dashboard (optional):

```bash
streamlit run streamlit_app.py
```

Additional features

- `/api/scrape` endpoint: POST JSON `{ "html": "<...>" }` to parse car listings via BeautifulSoup and return structured data.
- Streamlit UI includes create forms for brands, models, and cars and a scraper textarea.
- Dockerfile included to run the API in a container.

Docker

Build and run the app with Docker:

```bash
docker build -t car-management .
docker run -p 8000:8000 --env-file .env car-management
```

Seeding

Run the seeder to populate sample data:

```bash
python scripts/seed.py
```


Files of interest

- `app/db.py`: sqlite helper and schema init
- `app/schemas.py`: Pydantic models
- `app/auth.py`: API key authentication dependency
- `app/routers/cars.py`: CRUD API endpoints
- `streamlit_app.py`: simple dashboard placeholder
# car-management-system
Car Management System using FastAPI, Streamlit  &amp; SQLite.
