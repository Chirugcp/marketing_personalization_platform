from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.db.analytics import AnalyticsStore
from src.db.graph import InMemoryGraphStore
from src.db.vector_store import FaissVectorStore, UserCentroidIndex
from src.utils.config import settings
from src.utils.lineage import record_lineage
from src.utils.logger import get_logger
from src.utils.monitoring import track_latency
from src.utils.schemas import ConversationRecord
from src.utils.text_embedding import Embedder

logger = get_logger(__name__)


def load_records(path: str) -> list[ConversationRecord]:
    records: list[ConversationRecord] = []
    with open(path, 'r', encoding='utf-8') as fh:
        for line_no, line in enumerate(fh, start=1):
            try:
                records.append(ConversationRecord.model_validate(json.loads(line)))
            except Exception as exc:  # noqa: BLE001
                record_lineage('validation_error', {'line_no': line_no, 'error': str(exc)})
                logger.error('Validation failed on line %s: %s', line_no, exc)
    return records


def aggregate_counts(records: list[ConversationRecord]) -> list[tuple[str, str, int]]:
    counter = Counter((r.user_id, r.campaign_id) for r in records)
    return [(user_id, campaign_id, count) for (user_id, campaign_id), count in counter.items()]


def main() -> None:
    Path('sample_output').mkdir(exist_ok=True)
    logger.info('Pipeline started')

    with track_latency('load_records') as metrics:
        records = load_records(settings.data_path)
        metrics['record_count'] = len(records)
    if not records:
        logger.warning('No valid records found')
        record_lineage('anomaly', {'type': 'empty_input'})
        return

    with track_latency('embedding_generation') as metrics:
        embedder = Embedder()
        texts = [r.message for r in records]
        vectors = embedder.encode(texts)
        metrics['record_count'] = len(texts)
        metrics['embedding_dim'] = int(vectors.shape[1])
        if vectors.size == 0:
            record_lineage('anomaly', {'type': 'empty_embeddings'})
            raise RuntimeError('No embeddings generated')

    with track_latency('vector_index_upsert') as metrics:
        vector_store = FaissVectorStore(dim=vectors.shape[1])
        centroid_index = UserCentroidIndex()
        message_ids = [r.message_id for r in records]
        user_ids = [r.user_id for r in records]
        vector_store.upsert(message_ids, user_ids, vectors)
        centroids = centroid_index.update(user_ids, vectors)
        metrics['vector_rows'] = len(message_ids)
        metrics['distinct_users'] = len(centroids)

    with track_latency('graph_upsert') as metrics:
        graph_store = InMemoryGraphStore()
        graph_store.upsert_relationships([r.model_dump(mode='json') for r in records])
        metrics['relationship_records'] = len(records)

    with track_latency('analytics_upsert') as metrics:
        analytics = AnalyticsStore()
        aggregates = aggregate_counts(records)
        analytics.upsert_user_campaign_counts(aggregates)
        metrics['aggregate_rows'] = len(aggregates)

    with track_latency('cache_refresh') as metrics:
        metrics['status'] = 1  # placeholder for Redis session refresh in local prototype

    if any(not r.intent for r in records):
        record_lineage('anomaly', {'type': 'missing_relationships'})

    logger.info('Pipeline completed successfully with %s records', len(records))
    record_lineage('pipeline_complete', {'status': 'success', 'record_count': len(records)})


if __name__ == '__main__':
    main()
