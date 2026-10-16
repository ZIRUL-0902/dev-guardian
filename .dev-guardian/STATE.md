# Dev Guardian implementation handoff

Updated: 2026-10-16 (Asia/Taipei)
Task: implement/install portable dev-guardian and install Ponytail + default Taste skill.
Status: implemented; local verification executed; external guarantees remain explicitly unverified.

## Resume and source
- Skill: outputs/dev-guardian/SKILL.md; CLI: outputs/dev-guardian/scripts/guardian.py.
- Rules: root AGENTS.md; environment/decisions: neighboring Markdown files.
- Initial project was empty, with no user changes or application tests to preserve.
- Git: main; origin private ZIRUL-0902/dev-guardian. Previous verified HEAD: fa35be9ff50a74742680ca79f40f8f1ccd7b70a9.
- Verified tree SHA256: 054c41470fb051c3f0c4f0663fae6b45b78c243db12b4b01c0d07ec200d1d16a. Reconcile actual status on resume.
- Latest pre-publish local CLI evidence: .dev-guardian/evidence/20261016T150613.834989Z-db35107a5b/result.json (21 tests, no failures; source fingerprint in JSON).
- Latest format evidence: .dev-guardian/evidence/20261016T144058.458142Z-b1b0c99eeb/result.json.
- Prior evidence is historical after the publication commit; rerun checks on the committed revision or receiving device.
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
| Remote Linux/macOS CI matrix | external environment | PASSED | GitHub Actions 38921244577; four successful jobs |
| Windows | external environment | NOT TESTED | no Windows runner |
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
Read current result/log and reconcile actual source before further work. Repeat tests after changes/commits/environment updates. Initial delivery performed no push; GitHub publication is tracked in the task section below. No deployment or destructive Git operation.

## GitHub / SSH distribution task
- Scope: publish existing repository as ZIRUL-0902/dev-guardian (private by default), add SSH installation instructions, preserve prior records and user edits.
- Acceptance: authenticated repository creation, successful push, matching remote/local HEAD, clean fresh clone with skill/resources present and all 21 CLI tests passing.
- Remote SSH Codex runtime remains NOT TESTED until run on the user's actual host. No SSH server or target path supplied.
- Complete: private repository pushed at 0d09675016f7c389a4cb183f591d092831e01aa0; remote/local/fresh clone HEAD matched. Fresh-clone installation symlink and 21 tests passed.
- CI PASSED: run 38921244577, Ubuntu/macOS x Python 3.9/3.13, all four jobs success.
- Next: user runs outputs/SSH-INSTALL.md on their actual SSH host; authenticate GitHub there, then invoke $dev-guardian in Codex. Actual remote host discovery remains NOT TESTED.
- Publication status/report updates are documentation only; source code CI evidence is bound to 0d09675.
