from __future__ import annotations

from collections import defaultdict
from typing import Iterable

try:
    from neo4j import GraphDatabase
except Exception:  # noqa: BLE001
    GraphDatabase = None

from src.utils.config import settings


class GraphStore:
    def __init__(self) -> None:
        if GraphDatabase is None:
            raise RuntimeError('neo4j package is not installed')
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def upsert_relationships(self, records: Iterable[dict]) -> None:
        with self.driver.session() as session:
            for rec in records:
                session.run(
                    '''
                    MERGE (u:User {user_id: $user_id})
                    MERGE (c:Campaign {campaign_id: $campaign_id})
                    MERGE (i:Intent {intent: $intent})
                    MERGE (u)-[r:ENGAGED_WITH]->(c)
                    ON CREATE SET r.count = 1
                    ON MATCH SET r.count = r.count + 1
                    MERGE (u)-[:EXPRESSED]->(i)
                    MERGE (c)-[:TARGETS]->(i)
                    ''',
                    user_id=rec['user_id'],
                    campaign_id=rec['campaign_id'],
                    intent=rec['intent'],
                )

    def campaigns_for_users(self, user_ids: list[str]) -> dict[str, int]:
        if not user_ids:
            return {}
        with self.driver.session() as session:
            result = session.run(
                '''
                MATCH (u:User)-[r:ENGAGED_WITH]->(c:Campaign)
                WHERE u.user_id IN $user_ids
                RETURN c.campaign_id AS campaign_id, SUM(r.count) AS total_count
                ORDER BY total_count DESC
                ''',
                user_ids=user_ids,
            )
            return {row['campaign_id']: row['total_count'] for row in result}


class InMemoryGraphStore:
    def __init__(self) -> None:
        self.user_campaign_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def upsert_relationships(self, records: Iterable[dict]) -> None:
        for rec in records:
            self.user_campaign_counts[rec['user_id']][rec['campaign_id']] += 1

    def campaigns_for_users(self, user_ids: list[str]) -> dict[str, int]:
        campaign_counts: dict[str, int] = defaultdict(int)
        for user_id in user_ids:
            for campaign_id, cnt in self.user_campaign_counts.get(user_id, {}).items():
                campaign_counts[campaign_id] += cnt
        return dict(sorted(campaign_counts.items(), key=lambda item: (-item[1], item[0])))
