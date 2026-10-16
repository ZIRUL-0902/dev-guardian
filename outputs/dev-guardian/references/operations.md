# CLI, Git recovery and portability

Requires Python 3.9+ and Git, no Python dependencies. POSIX timeout cleanup uses a process group. Windows is NOT TESTED; automatic descendant cleanup is not guaranteed there. Commands below use `<skill>` as the actual skill folder and `<repo>` as the Git top-level directory. Run `--help` for flags.

## Initialize and run

```sh
python3 <skill>/scripts/guardian.py --root <repo> init
python3 <skill>/scripts/guardian.py --root <repo> snapshot
python3 <skill>/scripts/guardian.py --root <repo> plan
python3 <skill>/scripts/guardian.py --root <repo> verify --base <trusted-base-ref>
python3 <skill>/scripts/guardian.py --root <repo> run --id api-integration --level integration --timeout 120 -- python3 -m unittest tests.test_api
python3 <skill>/scripts/guardian.py --root <repo> check --ids api-integration
python3 <skill>/scripts/guardian.py --root <repo> record --id reader --level hardware --status BLOCKED --reason 'No physical reader available'
```

`record` intentionally exits 1. Invalid setup/input exits 2. Executed test failures return their nonzero code (signals normalized to 1); timeout exits 124, interrupted run 130, executable unavailable 127. Verify continues through selected tests then returns nonzero if any failed. Empty configuration cannot pass. Re-running init preserves records and appends the AGENTS block only once. Unique evidence/checkpoint directories avoid concurrent run collisions. STATE edits still require a single writer or normal Git merge conflict resolution.

Configure actual checks after inspecting tests/CI. Example only, **not a supplied passing test**:

```json
{"required_ids":["unit","reader"],"tests":[{"id":"unit","level":"unit","paths":["src/*","tests/*"],"argv":["python3","-m","unittest","discover","-s","tests"],"timeout":120}]}
```

`required_ids` binds the current acceptance matrix to `verify` and default `check`. It may include IDs such as `reader` that have no command: absence is NOT TESTED and a recorded blocker stays BLOCKED. Configured required tests always run even outside matching paths. Update this list when task scope changes, retaining unresolved requirements; do not remove blockers to pass a gate. An explicit `check --ids unit` verifies only that subset.

Patterns use Python fnmatch; `*` can match `/`. Deletions/renames, staged/unstaged/untracked and optional base-to-HEAD changes are included. Unknown impact or no changes runs all configured tests. Configuration edits themselves normally widen to all tests. Path matching cannot replace caller/dependency analysis. Configure critical journeys broadly or invoke them explicitly; do not shrink test selection to obtain green results. Shell expansion/pipelines are not performed. Commands can mutate data: inspect and use isolated fixtures/services; skill installation grants no permission to production actions.

## Checkpoints and recovery

```sh
python3 <skill>/scripts/guardian.py --root <repo> checkpoint --files src/example.py tests/test_example.py
```

Review individual file names first. A checkpoint writes selected staged and unstaged binary Git patches, a tar of current selected files (including selected untracked files), deletion list, source/environment snapshot and SHA256 manifest. Git index and working files are untouched. Symlinks (including parent directories), traversal, ignored paths, directories and obvious credential names are rejected. The filter is not a secret scanner: check selected contents and diffs yourself. Do not include secrets under arbitrary names. The manifest's presence denotes completion; verify its hashes before recovery. Backups omit unselected files, ignored data, submodules and external resources. Snapshot rejects submodules: capture each repository separately. Ignored generated code is outside the fingerprint; record its build inputs/environment separately.

Recover into a **new isolated checkout/worktree** at manifest HEAD after inspecting archive member names and verifying hashes. Apply nonempty `staged.patch` with `git apply --index`, then nonempty `unstaged.patch` with `git apply`; restore only reviewed untracked tar members and reconcile deletions from the manifest. The tar also holds complete current selected file content for manual recovery. For UNBORN HEAD, use a new empty repository. Never extract over the user's current tree or run reset/clean automatically. Test the recovered state before offering an overwrite/merge. The helper intentionally has no auto-restore operation.

## Evidence, secrets and volume

Evidence is `.dev-guardian/evidence/<UTC-and-unique-id>/{result.json,output.log}`. JSON records command argv (common-secret redaction), relative log path/hash, exit code/status, duration, before/after HEAD and working/index hash, host facts and truncation. The worktree test config and staged config/ENVIRONMENT are included in provenance; STATE/evidence/checkpoint updates are excluded. At most 64 KiB of sanitized log is saved per run; very long lines are omitted. Output is drained to prevent pipe deadlock. Do not use secret argv, dump environments, log PII, private keys or production data. Common token/password/Bearer/credential-URL patterns are redacted; **arbitrary secrets cannot be recognized reliably**. Review logs before sharing, and delete/revoke a leaked credential through the appropriate authorized process. No raw output, environment values, source copies or Git diffs are stored by snapshot/run.

Keep STATE short, search DECISIONS selectively, inspect newest result summaries before logs. Evidence accumulates deliberately; review old runs and archive resolved summaries when large. Never automatically delete the only failure or recovery evidence. Logs/checkpoint archives default to local Git ignores. To sync approved safe logs explicitly, inspect content then force-add only those specific files; hashes alone do not make unavailable logs independently reviewable. A receiving device must rerun checks if logs are missing or environment differs. Recovery archives are local and **not protected against loss of this disk**; use a reviewed encrypted backup when needed.

## Cross-device / cross-agent use

Commit the skill folder, project AGENTS.md, compact Markdown memory, config and reviewed evidence metadata. Copy the skill folder to `.agents/skills/dev-guardian` in another project, run init there and merge the rule into existing instructions. For Codex global discovery, copy the folder to `${CODEX_HOME:-$HOME/.codex}/skills/dev-guardian`; never overwrite an existing skill without comparison. This project installs a symlink to its source; after moving machines recreate the symlink (or copy) at the new path. Do not commit absolute symlinks as portable dependencies.

Claude/Gemini or another agent can read AGENTS.md + SKILL.md + STATE and run the same Python CLI. If its client does not load AGENTS automatically, explicitly supply that path through its supported project-rules mechanism. No Codex-only tools are needed. Actual sessions on other LLMs and remote CI must be validated externally; local tests do not establish those guarantees.
