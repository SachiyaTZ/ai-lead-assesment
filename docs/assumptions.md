# Assumptions and Trade-offs

- Hardcoded demo identities are acceptable for a POC; passwords are still hashed.
- The local document corpus is synthetic and designed to demonstrate overlapping evidence.
- Pinecone is represented through a production adapter and ingestion script; local dense retrieval is the default so the evaluator can run without paid credentials.
- Session memory is adequate for the required multi-turn demo; persistent memory is a production extension.
- MCP is lower priority in the assessment, so the core project uses an MCP-shaped enterprise-tool adapter with mock service catalog data.
- Reranking is not required for the core path; production can add a cross encoder/Cohere reranker with fail-open behavior.
- Human approval is documented as a production/bonus extension rather than blocking the core POC.
