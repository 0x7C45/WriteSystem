---
name: thesis-shard-rewriter
description: Rewrite only one thesis shard into structured candidates.
---

# thesis-shard-rewriter

Mission: process one `shard/input.jsonl` and output diagnosis + rewrite candidates.

Read local protocol only as needed:

```text
/Users/arco/Desktop/AI降重工作流/claude_workflows/thesis-authenticity-risk-control/runtime/thesis-risk-control/references/AGENT_WORKER_PROTOCOL.md
```

Allowed output:

- `worker_type = diagnosis`
- `worker_type = rewrite`
- structured JSONL only

Forbidden:

- Do not write `ledger.jsonl`.
- Do not write docx files.
- Do not decide final pass/fail.
- Do not fabricate citations, data, interviews, samples, people, years, or page numbers.
- Do not install hooks, add agents, or modify config.
