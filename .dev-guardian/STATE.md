# Dev Guardian implementation handoff

Updated: 2026-10-16 (Asia/Taipei)
Task: implement/install portable dev-guardian and install Ponytail + default Taste skill.
Status: implemented; local verification executed; external guarantees remain explicitly unverified.

## Resume and source
- Skill: outputs/dev-guardian/SKILL.md; CLI: outputs/dev-guardian/scripts/guardian.py.
- Rules: root AGENTS.md; environment/decisions: neighboring Markdown files.
- Initial project was empty, with no user changes or application tests to preserve.
- Git: main, local repository, no remote. Read actual HEAD/status/diffs; final evidence stores exact revision and dirty/index hash. Do not guess from this summary.
- Local global skill install is a symlink; installation details in outputs/installations.json.

## Progress and acceptance
| Criterion | Level | Status | Evidence |
| --- | --- | --- | --- |
| Non-overwriting init, real CLI/Git execution, success/failure/timeout/missing executable, stale/tampered evidence | integration | PASSED | 21-case test suite; current main result under evidence/ |
| Safe recovery, staged/unstaged/untracked handling, refused secrets/symlinks/traversal, literal filenames | integration | PASSED | real temporary Git repos and recovered worktree assertions |
| Impact selection incl. unknown paths, staged/unstaged cancellation, rename; required external blocker gate | integration | PASSED | suite + independent isolated reviewer probes |
| Bounded/redacted logs, descendant cleanup, concurrent evidence, portable copy | integration | PASSED | real subprocess/filesystem cases; no general secret-filter guarantee |
| Skill metadata/scaffold validity | static validation | PASSED | official quick_validate using isolated PyYAML venv |
| Explicit skill invocation, resume and corrected persistent handoff | local agent scenario | PASSED | outputs/validation/forward; historical gap subsequently corrected |
| Ponytail installation/enabled and isolated activation hook | install/local smoke | PASSED | outputs/installations.json; raw work/ logs local |
| Taste installed 29-file match, direction generator and real Chrome inspector | install/local smoke | PASSED | outputs/installations.json; one fixture action-button WARN |
| Automatic discovery in a subsequent Codex turn / actual Ponytail lifecycle hook | client execution | NOT TESTED | new turn/thread and upstream hook trust needed; Node absent from default PATH |
| Claude/Gemini/other model client and second physical device | external environment | NOT TESTED | independent local agent used available same model |
| Remote Linux/macOS CI matrix and Windows | external environment | NOT TESTED | CI supplied, no remote configured/run |
| Physical device/product external integration | hardware/integration | BLOCKED | no application/hardware/service supplied; no product acceptance claimed |

## Known failures and reliability
- No unresolved local test failure after fixes; detailed failure history in DECISIONS.
- Helpers cannot prove test quality or authenticity. Explicit check --ids is scoped; config required_ids must mirror task acceptance.
- STATE/evidence updates do not stale source evidence; config/environment do. Git commits change HEAD and require fresh checks.
- Review staged evidence for sensitive content before Git synchronization. Checkpoints/logs stay local by default; metadata alone is not independently sufficient without logs/rerun.

## Reviewed next commands (repository root)
```sh
git status --short --branch
python3 outputs/dev-guardian/scripts/guardian.py --root . snapshot
python3 outputs/dev-guardian/scripts/guardian.py --root . verify
python3 outputs/dev-guardian/scripts/guardian.py --root . check
```
Read current result/log and reconcile actual source before further work. Repeat tests after changes/commits/environment updates. No push, deployment or destructive Git operation was performed.
