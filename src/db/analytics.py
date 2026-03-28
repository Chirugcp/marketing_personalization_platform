from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from src.utils.config import settings


class AnalyticsStore:
    def __init__(self) -> None:
        Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(settings.sqlite_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self) -> None:
        self.conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS user_campaign_engagement (
                user_id TEXT NOT NULL,
                campaign_id TEXT NOT NULL,
                engagement_count INTEGER NOT NULL,
                PRIMARY KEY (user_id, campaign_id)
            )
            '''
        )
        self.conn.commit()

    def upsert_user_campaign_counts(self, rows: Iterable[tuple[str, str, int]]) -> None:
        self.conn.executemany(
            '''
            INSERT INTO user_campaign_engagement(user_id, campaign_id, engagement_count)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, campaign_id)
            DO UPDATE SET engagement_count = excluded.engagement_count
            ''',
            list(rows),
        )
        self.conn.commit()

    def fetch_campaign_rankings(self, user_ids: list[str]) -> list[dict]:
        if not user_ids:
            return []
        placeholders = ','.join('?' for _ in user_ids)
        query = f'''
            SELECT campaign_id, SUM(engagement_count) AS total_score
            FROM user_campaign_engagement
            WHERE user_id IN ({placeholders})
            GROUP BY campaign_id
            ORDER BY total_score DESC, campaign_id ASC
        '''
        rows = self.conn.execute(query, user_ids).fetchall()
        return [{'campaign_id': row[0], 'score': row[1]} for row in rows]
