# Reproducible environment

- Skill location (repository-relative): discover or vendor dev-guardian.
- Runtime / OS / architecture: NOT RECORDED; capture version commands.
- Package manager and build tools / versions: NOT RECORDED.
- Dependency lockfiles and versions / setup command: inspect manifests; never guess.
- Build / unit / integration / E2E commands: NOT RECORDED.
- CI configuration and required jobs: inspect repository.
- Local / CI / server differences: NOT RECORDED.
- Required services / test data / devices: name real boundaries and availability.
- Environment variable names: names only, NEVER values; document safe provisioning separately.
- Environment identity: runner captures basic host facts only; record container image digest, service/runtime versions, dependency lock hashes, target identity and hardware/firmware as relevant to the task. Rerun checks after any of these change; runner cannot detect remote changes.
