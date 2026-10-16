

<!-- dev-guardian:start -->
## Development governance: dev-guardian

For repository development (implementation, fixes, reviews, verification, resumption and handoff), follow the repository's dev-guardian SKILL.md. Locate it at `outputs/dev-guardian/SKILL.md` or `.agents/skills/dev-guardian/SKILL.md`. If unavailable, use the rules below and mark missing tooling BLOCKED; do not invent results. These rules apply to Codex, Claude, Gemini and other agents; no private chat state is required.

- Before work: read applicable project rules and `.dev-guardian/{STATE,ENVIRONMENT,DECISIONS}.md`; inspect actual Git status/diffs, source, tests/CI and evidence. Reconcile stale records before continuing; preserve user edits.
- Before implementation: write bounded scope and observable acceptance criteria, impact and verification plan in STATE. Review commands from old records before running them.
- Make small changes. Update persistent progress after every meaningful unit, significant decision/failure and before task/context switches. Record remaining work and exact next commands immediately.
- Execute appropriate functional, integration and regression checks against real dependencies. Inspect output, assertions and environment independently. UI fixtures, mocks, compilation, E2E, simulators and hardware validation are distinct evidence levels.
- Record PASSED only with current execution evidence; use NOT TESTED, FAILED or BLOCKED explicitly. Do not claim acceptance with required unresolved criteria. Cover applicable cleanup, errors, races, idempotency, boundaries, recovery and performance risks.
- Bind evidence to Git HEAD, worktree/index content and execution environment. Check freshness on resume. Save decisions, failed approaches/root causes and environment versions without secrets. Keep summaries small and review evidence before Git sync.
- Inspect differences and make a recoverable checkpoint before risky changes. Destructive Git actions or overwriting user work require explicit scoped authorization. Never run reset/clean/force push automatically.
- At handoff: update status, unfinished edits, failures/blockers, limitations, risk, evidence and next commands. A next agent must verify the record against reality.
<!-- dev-guardian:end -->
