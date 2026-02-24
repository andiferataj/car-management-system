from fastapi import FastAPI
from dotenv import load_dotenv
import os
import logging

load_dotenv()

from app.db import init_db
from app.routers.cars import router as cars_router
from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Car Management System")

# Allow local frontends (Streamlit) to access the API
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

from fastapi.responses import JSONResponse
from fastapi.requests import Request


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
def startup_event():
    # initialize DB (creates file and tables if needed)
    logger.info("Initializing database")
    init_db()

app.include_router(cars_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)), reload=True)
