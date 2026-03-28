# Scaling Plan

## 1) Handle 10M+ Users
### Storage Strategy
- Partition raw conversation storage by event date and tenant
- Archive cold events to object storage (GCS/S3) in Parquet
- Keep MongoDB only for hot operational windows
- Move analytical history to BigQuery partitioned tables

### Pipeline Strategy
- Replace local orchestrator with Airflow/Prefect + Kafka/PubSub
- Use micro-batching for embeddings
- Use idempotent message keys for replay safety
- Split workloads into:
  - ingest
  - embed
  - graph upsert
  - aggregate
  - cache refresh

### Compute Strategy
- Horizontal workers for embedding generation
- GPU-backed embedding workers only where ROI is clear
- Async sink writers to avoid N+1 DB latency

## 2) Ensure Sub-100 ms Vector Queries
- Use Milvus with HNSW or IVF_FLAT indexes
- Partition collections by tenant / region / campaign class
- Store user-centroid vectors rather than querying all message vectors for every request
- Cache top-N similar users for hot users in Redis
- Reduce payload size: return IDs and metadata, not full text
- Use colocated API and vector store in same region/VPC

## 3) Cost Efficiency in Cloud
- Batch BigQuery loads instead of row-level streaming where possible
- TTL old Redis keys aggressively
- Autoscale embedding workers based on queue depth
- Separate hot vs cold graph relationships
- Compress archival message data into Parquet
- Use approximate vector indexes tuned to latency/recall target
- Introduce feature flags to disable expensive enrichment during traffic spikes

## 4) Governance / Security
- PII tokenization before analytical export
- Row-level / tenant-level security in BigQuery
- Secrets in Secret Manager / Vault
- End-to-end audit logs for data access and pipeline runs
- Data contracts with schema registry

## 5) Production Roadmap
1. Replace SQLite with BigQuery
2. Replace FAISS with Milvus cluster
3. Introduce Kafka/PubSub ingestion
4. Add Airflow/Prefect orchestration
5. Add dbt for warehouse transformations
6. Add Prometheus/Grafana + alerting
7. Add CI/CD + Terraform + Docker Compose / Kubernetes
