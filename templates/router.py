from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import logging

from typing import List

from database.models import User
from auth.validation import get_current_auth_user
from config import configure_logging
from github_parse import parse_repos_github
from gitlab_parse import parse_repos_gitlab


router = APIRouter(tags=['Templates'])


templates = Jinja2Templates(directory='templates')


configure_logging()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def base(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/search")
async def search(query: str):
    query = query.lower()

    github_repos = await parse_repos_github(query)
    gitlab_repos = parse_repos_gitlab(query)

    github_repos_dict = [repo.dict() for repo in github_repos]
    gitlab_repos_dict = [repo.dict() for repo in gitlab_repos]

    return JSONResponse(content={
        "github_repos": github_repos_dict,
        "gitlab_repos": gitlab_repos_dict
    })


def sort_repositories(repos: List[dict]) -> List[dict]:
    return sorted(
            repos, 
            key=lambda x: (x.get("stars_count", 0), x.get("watchers_count", 0)),
            reverse=True
        )


@router.get("/authenticated/search")
async def authenticated_search(
    query: str,
    current_user: dict = Depends(get_current_auth_user)
):
    query = query.lower()

    github_repos = await parse_repos_github(query)
    gitlab_repos = parse_repos_gitlab(query)

    github_repos_dict = [repo.dict() for repo in github_repos]
    gitlab_repos_dict = [repo.dict() for repo in gitlab_repos]

    sorted_github_repos_dict = sort_repositories(github_repos_dict)
    sorted_gitlab_repos_dict = sort_repositories(gitlab_repos_dict)

    return JSONResponse(content={
        "github_repos": sorted_github_repos_dict,
        "gitlab_repos": sorted_gitlab_repos_dict
    })


@router.get("/authenticated/", response_class=HTMLResponse)
async def base(request: Request, current_user: User = Depends(get_current_auth_user)):
    return templates.TemplateResponse(request, "auth_index.html")


@router.get('/about_us', response_class=HTMLResponse)
async def get_base_page(request: Request):
    return templates.TemplateResponse(request, 'about_us.html')


@router.get('/jwt/register', response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse(request, 'register.html')


@router.get('/jwt/login/', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@router.get('/authenticated/', response_class=HTMLResponse)
async def get_auth_page(request: Request):
    return templates.TemplateResponse(request, 'authenticated.html')


