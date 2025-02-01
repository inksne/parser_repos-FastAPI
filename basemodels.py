from pydantic import BaseModel
from typing import Optional, List, Dict

class GitHubResponse(BaseModel):
    id: int
    name: str
    owner_name: str
    owner_id: int
    url: str
    type: str
    created_at: str
    updated_at: Optional[str] = None
    pushed_at: str
    size: int
    stars_count: int
    watchers_count: int
    language: Optional[str] = None
    license: Optional[Dict] = {}
    topics: Optional[List[str]] = []
    forks: int
    default_branch: str


class GitLabResponse(BaseModel):
    id: int
    name: str
    owner_name: str
    owner_id: int
    url: str
    created_at: str
    updated_at: str
    last_activity_at: str
    stars_count: int
    forks_count: int
    license: Optional[Dict] = {}
    topics: Optional[List[str]] = []
    forks: int
    default_branch: str