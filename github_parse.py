from fastapi import APIRouter

import httpx
import logging
import json

from database.database import r
from config import get_connection, configure_logging, GITHUB_ACCESS_TOKEN
from exceptions import server_exc
from basemodels import GitHubResponse
from rabbitmq import produce_message

from typing import List


configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=['GitHub'])


@router.get('/github', response_model=List[GitHubResponse])
async def parse_repos_github(query: str):
    cached_data = r.get(f'github_{query}')
    if cached_data:
        logger.info('данные найдены в редисе (GitHub)')
        items = json.loads(cached_data)
    else:
        logger.info('данные не найдены в редисе (GitHub)')
        url = f'https://api.github.com/search/repositories?q={query}'
        headers = {'Authorization': GITHUB_ACCESS_TOKEN}
        async with httpx.AsyncClient() as client:
            try:
                logger.info('делаем запрос к GitHub')
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                logger.info(f'статус код: {response.status_code}')
                items = response.json().get("items", [])
                logger.info(f'получено: {items}')

                r.set(f'github_{query}', json.dumps(items))  
                r.expire(f'github_{query}', 1800)
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                logger.error(e)
                raise server_exc

    repos = [
        GitHubResponse(
            id=item["id"],
            name=item["name"],
            owner_name=item["owner"]["login"],
            owner_id=item["owner"]["id"],
            url=item["html_url"],
            type=item["owner"]["type"],
            created_at=item["created_at"],
            updated_at=item.get("updated_at"),
            pushed_at=item["pushed_at"],
            size=item["size"],
            stars_count=item["stargazers_count"],
            watchers_count=item["watchers_count"],
            language=item["language"],
            license=item.get("license", {}),
            topics=item["topics"],
            forks=item["forks_count"],
            default_branch=item["default_branch"]
        )
        for item in items
    ]

    message_body = f"парсинг Github завершен успешно для запроса '{query}'"
    with get_connection() as connection:
        with connection.channel() as channel:
            produce_message(channel=channel, message_body=message_body)

    return repos