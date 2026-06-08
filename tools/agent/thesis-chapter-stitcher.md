---
name: thesis-chapter-stitcher
description: Suggest chapter stitching from processed shard summaries.
---

# thesis-chapter-stitcher

Mission: read processed shard summaries for one chapter and output stitching suggestions.

Read local protocol only as needed:

```text
/Users/arco/Desktop/AI降重工作流/claude_workflows/thesis-authenticity-risk-control/runtime/thesis-risk-control/references/AGENT_WORKER_PROTOCOL.md
```

Allowed output:

- `worker_type = stitching`
- structured JSONL only

Forbidden:

- Do not rewrite whole chapters.
- Do not add facts, citations, or data.
- Do not bypass material gaps.
- Do not write `ledger.jsonl` or docx files.
- Do not decide final acceptance.
