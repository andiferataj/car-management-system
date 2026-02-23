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

Files of interest

- `app/db.py`: sqlite helper and schema init
- `app/schemas.py`: Pydantic models
- `app/auth.py`: API key authentication dependency
- `app/routers/cars.py`: CRUD API endpoints
- `streamlit_app.py`: simple dashboard placeholder
# car-management-system
Car Management System using FastAPI, Streamlit  &amp; SQLite.
