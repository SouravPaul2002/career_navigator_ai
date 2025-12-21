from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.career.career_routes import router as career_router
from routes.users.user_routes import router as users_router
from routes.common.common_routes import router as common_router
from database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the route routers
app.include_router(career_router, prefix="/career", tags=["career"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(common_router, tags=["common"])