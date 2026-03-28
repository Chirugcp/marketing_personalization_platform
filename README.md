# Founding Data Engineer Take-Home Assignment

## Overview
This submission implements a modular mini data platform for AI-driven marketing personalization with:
- **Operational store**: MongoDB for raw conversations + metadata
- **Cache**: Redis for recent user sessions and low-latency reads
- **Vector store**: FAISS-based local prototype with a production-ready adapter pattern for Milvus
- **Graph store**: Neo4j for user-campaign-intent relationships
- **Analytics store**: SQLite for aggregated engagement metrics (BigQuery-ready schema)
- **API**: FastAPI hybrid retrieval endpoint
- **Pipeline orchestration**: Python DAG-style workflow with validation, lineage, logging, and anomaly detection

> Note: The assignment explicitly names Milvus. For a lightweight, reproducible local prototype, the implementation uses a **VectorStore interface** with a **FAISS backend** by default and a documented **Milvus production migration path**. The architecture and scaling plan assume Milvus in production.

## Project Structure
```text
├── src/
│   ├── pipeline/
│   │   ├── generate_sample_data.py
│   │   └── run_pipeline.py
│   ├── api/
│   │   └── main.py
│   ├── db/
│   │   ├── analytics.py
│   │   ├── graph.py
│   │   ├── mongo_store.py
│   │   ├── redis_cache.py
│   │   └── vector_store.py
│   └── utils/
│       ├── config.py
│       ├── lineage.py
│       ├── logger.py
│       ├── monitoring.py
│       ├── schemas.py
│       └── text_embedding.py
├── data/
│   └── sample_conversations.jsonl
├── sample_output/
│   ├── lineage.jsonl
│   ├── pipeline.log
│   └── analytics.db
├── architecture.md
├── architecture_diagram.md
├── scaling_plan.md
└── requirements.txt
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Optional Infrastructure
You can connect real services using environment variables:
- `MONGO_URI`
- `REDIS_HOST`, `REDIS_PORT`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `VECTOR_BACKEND=faiss|milvus`
- `SQLITE_PATH`

If external services are unavailable, the code still demonstrates architecture, models, lineage, and ranking logic.

## Run Sample Data Generation
```bash
python -m src.pipeline.generate_sample_data
```

## Run the Pipeline
```bash
python -m src.pipeline.run_pipeline
```

Pipeline outputs:
- Raw conversations persisted
- Embeddings generated and indexed
- Graph relationships created
- Aggregates written to SQLite
- Lineage + latency + anomalies logged

## Run the API
```bash
uvicorn src.api.main:app --reload
```

### Example
```bash
curl http://127.0.0.1:8000/recommendations/user_001
```

## Design Choices
1. **Polyglot persistence by workload**
   - MongoDB: write-heavy conversation documents
   - Redis: hot session cache
   - Vector index: ANN similarity search
   - Neo4j: campaign and intent traversal
   - SQLite/BigQuery: aggregations and ranking

2. **Adapter pattern for storage systems**
   - Keeps orchestration logic decoupled from specific engines
   - Enables local reproducibility and production migration

3. **Lineage and observability are first-class**
   - Every stage records run metadata, record counts, durations, and anomalies

4. **Separation of online and offline paths**
   - Real-time path for session cache + vector lookup
   - Batch path for aggregation and graph enrichment

## What I Would Show HR / Reviewer
- Clean modular project layout
- Runnable pipeline + API
- Architecture aligned to real production scaling
- Explicit trade-offs between prototype and production
- Strong operational thinking: validation, idempotency, anomalies, lineage, caching, and indexing
