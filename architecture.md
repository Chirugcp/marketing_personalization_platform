# Architecture Justification

## Goal
Design a modular multi-database data platform that supports ingestion, embeddings, graph relationships, analytics, caching, and low-latency recommendations.

## System Overview
The platform separates responsibilities by access pattern:

### 1. Ingestion Layer
- Source: user chat events (`user_id`, `campaign_id`, `message_id`, `message`, `intent`, `timestamp`)
- Entry point: JSONL/CSV or streaming API
- Validation: Pydantic schema validation before persistence
- Immediate persistence: MongoDB for raw, immutable event documents

### 2. Embedding Layer
- Model: `sentence-transformers`
- Output: dense numeric embedding for each conversation message
- Checks:
  - empty text
  - embedding dimension mismatch
  - duplicate message IDs

### 3. Vector Layer
- Prototype: FAISS for local reproducibility
- Production: Milvus with IVF/HNSW index, partitions, and metadata filters
- Purpose: nearest-neighbor user/message retrieval for personalization

### 4. Graph Layer
- Neo4j stores:
  - `(:User)`
  - `(:Campaign)`
  - `(:Intent)`
  - relationships like `[:ENGAGED_WITH]`, `[:EXPRESSED]`
- Purpose: traversing semantic user-campaign relationships not easily expressible in relational SQL

### 5. Analytics Layer
- SQLite in prototype, BigQuery in production
- Stores aggregated metrics:
  - user_campaign_engagement
  - campaign engagement counts
  - intent frequencies
- Purpose: ranking, reporting, trend analysis

### 6. Cache Layer
- Redis caches recent user sessions and precomputed recommendation payloads
- TTL-based eviction reduces latency for hot users

## Why This Multi-DB Pattern Is Correct
| Need | Best-fit Store | Why |
|---|---|---|
| Raw semi-structured conversations | MongoDB | Flexible schema, operational writes |
| Recent hot sessions | Redis | Sub-millisecond cache access |
| Embedding similarity | Milvus / FAISS | ANN search optimized for vectors |
| Relationship traversal | Neo4j | Native graph traversal for user-campaign-intent links |
| Aggregations and ranking | BigQuery / SQLite | SQL analytics and efficient rollups |

## Real-Time vs Batch Separation
### Real-Time
- Ingest event
- Cache user session in Redis
- Generate embedding for new message
- Upsert vector entry
- Optional recommendation refresh

### Batch
- Rebuild aggregates
- Backfill graph edges
- Data quality audits
- Cost-controlled analytics sync to BigQuery

## Fault Tolerance / Reliability Strategy
- Retry with backoff per sink
- Sink isolation to prevent one DB failure from blocking all writes
- Lineage records for replay/debugging
- Dead-letter capture for validation failures
- Idempotent writes using `message_id`

## Production Trade-Offs
- Prototype keeps local setup simple with SQLite + FAISS
- Production uses BigQuery + Milvus for true scale
- Interface-based implementation avoids rewrite of orchestration code
