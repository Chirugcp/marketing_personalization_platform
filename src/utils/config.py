from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    mongo_db: str = os.getenv('MONGO_DB', 'marketing_platform')
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    neo4j_uri: str = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user: str = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password: str = os.getenv('NEO4J_PASSWORD', 'password')
    sqlite_path: str = os.getenv('SQLITE_PATH', 'sample_output/analytics.db')
    embedding_model: str = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    vector_backend: str = os.getenv('VECTOR_BACKEND', 'faiss')
    vector_dim: int = int(os.getenv('VECTOR_DIM', '384'))
    lineage_path: str = os.getenv('LINEAGE_PATH', 'sample_output/lineage.jsonl')
    log_path: str = os.getenv('LOG_PATH', 'sample_output/pipeline.log')
    data_path: str = os.getenv('DATA_PATH', 'data/sample_conversations.jsonl')
    top_k_similar_users: int = int(os.getenv('TOP_K_SIMILAR_USERS', '5'))
    recommendation_cache_ttl_sec: int = int(os.getenv('RECOMMENDATION_CACHE_TTL_SEC', '300'))


settings = Settings()
