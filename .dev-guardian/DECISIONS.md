# Decisions and failure memory

## 2026-10-16: portable governance in an empty project
- Keep one skill source at outputs/dev-guardian, three Markdown memory files, JSON test/acceptance config and one standard-library CLI. No database, daemon, private Codex API or external service dependency.
- Vendored source and AGENTS are Git-portable. Local discoverability uses an explicit symlink; another machine must recreate it or copy the skill.
- Checkpoints use reviewed individual files, independent staged/unstaged patches, current-file tar and hashes; no auto-restore or Git index mutation. Recovery validated in an isolated worktree.
- Evidence is a local consistency record, not a signed attestation. Generic commands can be misleading; an agent must inspect assertions, skip counts, real dependencies and acceptance scope.

## 2026-10-16: observed failures and corrections
- Initialization creates untracked AGENTS. First path-selection test accidentally expected narrow scope despite that unknown-impact file. Corrected its fixture baseline; kept conservative all-tests behavior.
- Config worktree edits originally did not stale evidence: reproduced failing test, included config content. ENVIRONMENT content is hashed without storing variable values.
- Independent forward agent showed unit-only config can pass despite external blockers. Added required_ids to bind commandless acceptance criteria to verify/default check. Missing and BLOCKED required IDs now keep gate nonzero; explicit --ids remains scoped.
- Independent code review reproduced Authorization scheme-token leakage, long-line suffix leakage, cancellation between staged/unstaged hiding impact, and excluded staged config fingerprint. Added regression checks and corrected each behavior.
- Follow-up review found rename detection hid old path. Changed impact diffs to --no-renames; staged and base-to-HEAD rename probes now include both paths.
- Reviewers independently reran corrections. Local suite: 21 behavioral CLI/Git/filesystem tests. See evidence result.json/log for final current-source run.
- Baseline no-skill evaluator already avoided false completion; no demonstrated comparative behavioral improvement is claimed. Forward evaluation exercised explicit skill use, real checks, persistent handoff, stale evidence and blocker reporting.

## Remaining limitations
- No automatic proof of test quality, arbitrary secret detection, authenticity, agent obedience or full dependency graph. Path matching is advisory; inspect callers and critical journeys.
- Root .dev-guardian config/environment fingerprints are covered; remote services, dependency installations, containers and firmware changes require explicit environment records/reruns.
- Unselected/ignored checkpoint files are not backed up; local archives do not survive disk loss. No destructive recovery tested against user data.
- Historical forward fixture artifacts under outputs/validation/forward reflect the earlier assessment; default-gate gap shown there was subsequently fixed with required_ids and tested. Those artifacts are not current main-project evidence.
- New-client automatic discovery, actual Claude/Gemini execution, remote CI/second device, physical hardware and real external product integration remain unverified.
