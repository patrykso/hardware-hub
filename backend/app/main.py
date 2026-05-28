from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from .database import Base, SessionLocal, engine
from .seed import seed_database


def _initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_in_threadpool(_initialize_database)
    yield


app = FastAPI(
    title="Hub Rental API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
