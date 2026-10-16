# Reproducible environment

- Project: initially empty directory; no existing application, tests, CI or ancestor AGENTS found. Git initialized on main for local synchronization; no remote configured.
- Source skill: outputs/dev-guardian (tracked). Local Codex install is ~/.codex/skills/dev-guardian symlink to this source. Recreate on another device or copy the folder; do not depend on the absolute link.
- Runtime tested: macOS Darwin arm64; /usr/bin/python3 3.9.6; Git 2.54.0 (Apple Git-157). Runtime helper/tests use Python standard library only; minimum Python 3.9.
- Setup: python3 outputs/dev-guardian/scripts/guardian.py --root . init (non-overwriting).
- Tests: python3 outputs/dev-guardian/tests/test_guardian.py
- Evidence run: python3 outputs/dev-guardian/scripts/guardian.py --root . verify
- Required acceptance IDs: guardian-cli (local CLI integration). No application/product behavior is supplied by this repository.
- Skill metadata validation: work/validator-env/bin/python /Users/ryanliu/.codex/skills/.system/skill-creator/scripts/quick_validate.py outputs/dev-guardian. This development-only venv uses PyYAML 6.0.3; absent from system and bundled Python. Not a runtime dependency.
- CI: .github/workflows/dev-guardian.yml; Ubuntu/macOS x Python 3.9/3.13. Jobs defined; NOT TESTED on remote runner. No external deployment/remote target.
- Server/Linux/Windows and other LLM clients: NOT TESTED. Independent local fresh agent pass used same available model, not Claude/Gemini.
- Third-party installations: see outputs/installations.json, with pinned Taste commit and inspected Ponytail commit/version.
- Bundled Node tested: v24.19.0, executable at ~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node. Default shell PATH has no node. Use explicit executable or add that directory to PATH for these scripts; lifecycle hook environment remains NOT TESTED.
- Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome; Taste isolated real-browser inspector passed with one WARN (no action button on smoke fixture).
- Required variable names for isolated Ponytail smoke: PLUGIN_DATA, CLAUDE_PLUGIN_ROOT, PONYTAIL_MAP. No secrets required or recorded. Real client hook trust is not bypassed.
- Hardware and external product services: absent; hardware/external integration acceptance BLOCKED, not implied by this skill's CLI tests.
