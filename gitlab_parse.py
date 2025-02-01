from fastapi import APIRouter

import requests
import logging
import json

from database.database import r
from config import get_connection, configure_logging, GITLAB_ACCESS_TOKEN
from exceptions import server_exc
from basemodels import GitLabResponse
from rabbitmq import produce_message


configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=['GitLab'])

@router.get('/gitlab')
def parse_repos_gitlab(query: str):
    cached_data = r.get(f'gitlab_{query}')
    if cached_data:
        logger.info('данные найдены в редисе (GitLab)')
        items = json.loads(cached_data)
    else:
        logger.info('данные не найдены в редисе (GitLab)')
        url = f'https://gitlab.com/api/v4/projects?search={query}'
        headers = {'Authorization': f'Bearer {GITLAB_ACCESS_TOKEN}'}

        try:
            logger.info('делаем запрос к GitLab')
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logger.info(f'статус код: {response.status_code}')
            items = response.json()
            logger.info(f'получено: {items}')

            r.set(f'gitlab_{query}', json.dumps(items))  
            r.expire(f'gitlab_{query}', 1800)
        except (requests.exceptions.HTTPError, Exception) as e:
            logger.error(e)
            raise server_exc

    repos = [
        GitLabResponse(
            id=item["id"],
            name=item["name"],
            owner_name=item["namespace"]["name"],
            owner_id=item["namespace"]["id"],
            url=item["web_url"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            last_activity_at=item["last_activity_at"],
            stars_count=item["star_count"],
            forks_count=item["forks_count"],
            license=item.get("license", {}),
            topics=item.get("tag_list"),
            forks=item["forks_count"],
            default_branch=item["default_branch"]
        )
        for item in items
    ]

    message_body = f"парсинг GitLab завершен успешно для запроса '{query}'"
    with get_connection() as connection:
        with connection.channel() as channel:
            produce_message(channel=channel, message_body=message_body)

    return repos