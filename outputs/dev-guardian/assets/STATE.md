# Development state

Updated UTC: not recorded yet
Task status: NOT STARTED (not a verification result)
Scope and observable acceptance criteria: establish before implementation.

## Resume
- Source/skill location: record repository-relative paths.
- Git HEAD / branch / tree SHA256: run snapshot; do not guess.
- User-owned edits / ongoing files: inspect staged, unstaged and untracked paths.
- Baseline tests / CI: inspect; NOT TESTED until executed.

## Progress
- Completed: none recorded.
- In progress: none recorded.
- Remaining: inspect project and define a bounded task.

## Acceptance and evidence
Keep config.json required_ids synchronized with the required acceptance rows.
| Criterion | Required level / real dependency | Status | Evidence / reason |
| --- | --- | --- | --- |
| Baseline behavior | Define from project | NOT TESTED | No execution recorded |

## Failures, blockers and risks
- Record observed error, reproduction, root cause or uncertainty, user impact and recovery.
- Reliability review: errors, cleanup, concurrency, idempotency, boundaries, recovery, performance; mark applicable checks.

## Next actions
1. Read rules, this file, ENVIRONMENT and relevant DECISIONS.
2. Inspect Git/source and reconcile evidence; review commands before execution.
3. Write exact safe commands here after discovering the real project.
