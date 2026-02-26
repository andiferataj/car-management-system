from fastapi import FastAPI
from database import init_db
from routers import users, cars

init_db()

app = FastAPI(
    title="🚗 Car Management System",
    description="Manage users and cars with full CRUD.",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(cars.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Car Management API is running 🚗"}
