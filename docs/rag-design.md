# Hybrid RAG Design

Dense retrieval captures semantic similarity while BM25-style sparse scoring preserves exact enterprise vocabulary, incident IDs and service names. Scores are normalized to comparable ranges and combined using configurable weights. Metadata filters are applied before scoring, and results carry stable document/chunk attribution.

For a credential-free demo the repository uses deterministic hash embeddings. The Pinecone adapter/ingestion path is included for the required vector database. Production should use Pinecone as the dense index, retain a sparse index (Pinecone sparse vectors or a dedicated BM25 engine), then fuse and optionally rerank results.
