from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from src.database import create_tables
from src.api import main_router
from src.middleware import (
    CheckRequestsMiddleware,
    BasicAuthBackend,
    AuthenticationMiddleware,
    AuthMiddleware,
    GetMeMiddleware
)



@asynccontextmanager
async def lifespan(app: FastAPI):
	await create_tables()
	yield

app = FastAPI(
    title="TeaTime",
    lifespan=lifespan,
    prefix="/api"
)
app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
app.add_middleware(CheckRequestsMiddleware)
app.add_middleware(AuthenticationMiddleware, BasicAuthBackend())
app.add_middleware(AuthMiddleware)
app.add_middleware(GetMeMiddleware)
