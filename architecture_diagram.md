# Architecture Diagram

```mermaid
flowchart LR
    A[Chat Events JSONL / API / Stream] --> B[Validation + Orchestrator]
    B --> C[MongoDB Raw Conversations]
    B --> D[Sentence Transformer Embedding]
    D --> E[Vector Store: FAISS Prototype / Milvus Prod]
    B --> F[Neo4j Graph Builder]
    B --> G[Aggregation Job]
    G --> H[SQLite Prototype / BigQuery Prod]
    B --> I[Redis Session Cache]

    C --> J[Lineage + Monitoring]
    D --> J
    E --> J
    F --> J
    H --> J
    I --> J

    K[FastAPI Recommendation API] --> I
    K --> E
    K --> F
    K --> H
    K --> L[Top Campaign Recommendations]
```

## Flow Notes
1. User chat events enter the orchestrator.
2. Data is schema-validated and written to MongoDB.
3. Text is embedded and pushed to the vector store.
4. Relationships between users, campaigns, and intents are updated in Neo4j.
5. Batch aggregation writes engagement metrics to SQLite/BigQuery.
6. Recent sessions are cached in Redis.
7. The API composes vector + graph + analytics for hybrid recommendations.
