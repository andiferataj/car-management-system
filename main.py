from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from app.db import init_db
from app.routers.cars import router as cars_router

app = FastAPI(title="Car Management System")


@app.on_event("startup")
def startup_event():
    # initialize DB (creates file and tables if needed)
    init_db()

app.include_router(cars_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)), reload=True)
