from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



from .routers.auth import router as auth_router
from .routers.equipment import router as equipment_router
from .routers.users import router as users_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(equipment_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

