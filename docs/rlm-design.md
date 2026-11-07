# Simplified Recursive Language Model / Research Design

This POC demonstrates an RLM-style investigation pattern, not a full research reproduction.

```text
complex query
→ classify + scope
→ targeted retrieval
→ bounded decomposition into batches
→ independent batch analysis
→ aggregate recurring signals
→ deduplicate evidence
→ citation verification
→ final answer
```

Controls: `MAX_RECURSION_DEPTH`, `MAX_RESEARCH_SUBTASKS`, `MAX_DOCUMENTS_PER_STEP`, and `MAX_TOTAL_TOKENS`. A failed subtask should contribute an error record rather than silently poisoning parent conclusions; aggregation only uses successful, attributable evidence. This contains the “butterfly effect” of an early bad sub-result.
