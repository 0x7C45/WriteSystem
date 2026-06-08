---
name: thesis-risk-control
description: Explicit launcher for the isolated thesis risk-control workflow.
---

# Thesis Risk Control Launcher

Use only when the user explicitly asks for `thesis-risk-control`, `论文工作流`, `AUTO_LAUNCH`, or `AUTO_RUN`.

This is a launcher, not a general thesis-writing assistant.

Read first:

```text
/Users/arco/Desktop/AI降重工作流/claude_workflows/thesis-authenticity-risk-control/runtime/AUTO_LAUNCH.md
```

Hard boundaries:

- Real tasks must start with `AUTO_BOOT`.
- Full-document work must use `FULL_SHARDED_RUN`.
- Do not bypass `ledger.jsonl`, `worker-output-log.jsonl`, reducer checks, or report consistency gates.
- Do not generate `revised_thesis.docx` unless the local workflow later explicitly opens the final gate.
- Do not install hooks, modify settings, edit memory, or copy long workflow rules into global context.

Local workflow root:

```text
/Users/arco/Desktop/AI降重工作流/claude_workflows/thesis-authenticity-risk-control/runtime/
```
