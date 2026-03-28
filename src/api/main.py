from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, HTTPException

from src.db.analytics import AnalyticsStore
from src.db.graph import InMemoryGraphStore
from src.db.vector_store import FaissVectorStore, UserCentroidIndex
from src.utils.config import settings
from src.utils.schemas import ConversationRecord
from src.utils.text_embedding import Embedder

app = FastAPI(title='Hybrid Retrieval API', version='1.0.0')


class RecommendationService:
    def __init__(self) -> None:
        self.analytics = AnalyticsStore()
        self.graph = InMemoryGraphStore()
        self.vector_store: FaissVectorStore | None = None
        self.user_centroids: dict[str, object] = {}
        self.user_latest_message: dict[str, str] = {}
        self.embedder = Embedder()
        self._bootstrap_from_file()

    def _bootstrap_from_file(self) -> None:
        if not Path(settings.data_path).exists():
            return
        records: list[ConversationRecord] = []
        with open(settings.data_path, 'r', encoding='utf-8') as fh:
            for line in fh:
                records.append(ConversationRecord.model_validate(json.loads(line)))
        if not records:
            return
        vectors = self.embedder.encode([r.message for r in records])
        self.vector_store = FaissVectorStore(dim=vectors.shape[1])
        centroid_index = UserCentroidIndex()
        self.vector_store.upsert(
            [r.message_id for r in records],
            [r.user_id for r in records],
            vectors,
        )
        self.user_centroids = centroid_index.update([r.user_id for r in records], vectors)
        self.graph.upsert_relationships([r.model_dump(mode='json') for r in records])
        counts: dict[tuple[str, str], int] = defaultdict(int)
        for r in records:
            counts[(r.user_id, r.campaign_id)] += 1
            self.user_latest_message[r.user_id] = r.message
        self.analytics.upsert_user_campaign_counts(
            [(u, c, cnt) for (u, c), cnt in counts.items()]
        )

    def get_recommendations(self, user_id: str) -> dict:
        if user_id not in self.user_centroids:
            raise HTTPException(status_code=404, detail=f'user_id {user_id} not found')
        if self.vector_store is None:
            raise HTTPException(status_code=500, detail='vector store unavailable')

        similar_users = [u for u in self.vector_store.similar_users(self.user_centroids[user_id], settings.top_k_similar_users + 1) if u != user_id][:5]
        graph_campaigns = self.graph.campaigns_for_users(similar_users)
        analytics_campaigns = self.analytics.fetch_campaign_rankings(similar_users)

        merged_scores: dict[str, int] = defaultdict(int)
        for campaign_id, score in graph_campaigns.items():
            merged_scores[campaign_id] += int(score)
        for row in analytics_campaigns:
            merged_scores[row['campaign_id']] += int(row['score'])

        ranked = [
            {'campaign_id': campaign_id, 'score': score}
            for campaign_id, score in sorted(merged_scores.items(), key=lambda item: (-item[1], item[0]))
        ]

        return {
            'user_id': user_id,
            'similar_users': similar_users,
            'recommendations': ranked[:5],
            'explanation': 'Ranked by vector similarity -> graph expansion -> analytics engagement score',
        }


service = RecommendationService()


@app.get('/health')
def health() -> dict:
    return {'status': 'ok'}


@app.get('/recommendations/{user_id}')
def recommendations(user_id: str) -> dict:
    return service.get_recommendations(user_id)
