from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.database import create_db_and_tables

from github_parse import router as gh_router
from gitlab_parse import router as gl_router
from auth.auth import router as auth_router
from templates.router import router as template_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title='parser_repos')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(gh_router)
app.include_router(gl_router)
app.include_router(template_router)
app.include_router(auth_router)