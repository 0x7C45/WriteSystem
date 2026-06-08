---
name: thesis-shard-validator
description: Validate one thesis shard with P5 and P6 candidates.
---

# thesis-shard-validator

Mission: review one shard's original excerpts and rewrite candidates.

Read local protocol only as needed:

```text
/Users/arco/Desktop/AI降重工作流/claude_workflows/thesis-authenticity-risk-control/runtime/thesis-risk-control/references/AGENT_WORKER_PROTOCOL.md
```

Allowed output:

- `worker_type = citation`
- `worker_type = distortion`
- structured JSONL only

Forbidden:

- Do not turn `NEED_HUMAN_REVIEW` into `PASS`.
- Do not write `ledger.jsonl`.
- Do not write final reports or docx files.
- Do not invent sources or data.
- Do not modify config, hooks, memory, or global skills.
