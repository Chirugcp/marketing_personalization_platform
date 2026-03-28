from __future__ import annotations

import json

import redis

from src.utils.config import settings


class SessionCache:
    def __init__(self) -> None:
        self.client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    def set_recent_session(self, user_id: str, payload: dict, ttl_sec: int = 3600) -> None:
        self.client.setex(f'session:{user_id}', ttl_sec, json.dumps(payload))

    def get_recent_session(self, user_id: str) -> dict | None:
        value = self.client.get(f'session:{user_id}')
        return json.loads(value) if value else None

    def set_recommendations(self, user_id: str, payload: dict) -> None:
        self.client.setex(
            f'reco:{user_id}',
            settings.recommendation_cache_ttl_sec,
            json.dumps(payload),
        )

    def get_recommendations(self, user_id: str) -> dict | None:
        value = self.client.get(f'reco:{user_id}')
        return json.loads(value) if value else None
