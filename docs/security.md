# Security

- **Authentication:** signed JWTs for POC users; production should use OIDC/SSO.
- **RBAC:** centralized deterministic permission matrix. Every privileged tool invocation calls `authorize()` before execution.
- **Prompt injection:** high-signal override, exfiltration, role-escalation and secret-reveal patterns are blocked before the graph.
- **Retrieved content:** always treated as untrusted data. Embedded document instructions are flagged/sanitized and never promoted to system instructions.
- **Tool safety:** controlled analytics operations only; no user supplied `eval`, shell or arbitrary Python.
- **Citation integrity:** every bracketed document ID in a generated answer must occur in the retrieved evidence set.
- **Validation:** Pydantic bounds message length, date ranges and `top_k`; analysis fields and operations are allowlisted.
- **Rate limiting:** independent per-user token bucket returns a clean 429.
- **Secrets:** `.env` is ignored; credentials should come from a cloud secret manager in production.
- **Logging hygiene:** structured logs must not include passwords, bearer tokens or API keys.
