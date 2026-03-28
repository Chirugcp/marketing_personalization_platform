from __future__ import annotations

from typing import Iterable

from pymongo import MongoClient, UpdateOne

from src.utils.config import settings


class MongoConversationStore:
    def __init__(self) -> None:
        self.client = MongoClient(settings.mongo_uri)
        self.collection = self.client[settings.mongo_db]['conversations']
        self.collection.create_index('message_id', unique=True)
        self.collection.create_index('user_id')
        self.collection.create_index('campaign_id')
        self.collection.create_index('timestamp')

    def upsert_many(self, records: Iterable[dict]) -> int:
        operations = [
            UpdateOne({'message_id': rec['message_id']}, {'$set': rec}, upsert=True)
            for rec in records
        ]
        if not operations:
            return 0
        result = self.collection.bulk_write(operations, ordered=False)
        return result.upserted_count + result.modified_count
