# Acceptance and evidence contract

Choose checks from the actual change and its consumers, not from a fixed test count.

| Change surface | Typical regression and reliability checks |
| --- | --- |
| Pure logic | Real inputs/outputs; boundary, invalid and large inputs; existing unit suite |
| API / persistence | Real service/database in an isolated test environment; schema compatibility, transaction rollback, failure and retry |
| UI journey | Real user actions through frontend/backend; reload/persistence and failure state; assert resulting state, not just screenshot |
| Async / resource ownership | Cancellation, timeouts, cleanup, concurrent callers, repeated requests, duplicate suppression |
| Device / native code | Build, simulator, real integration and physical device matrix reported separately; disconnect/reconnect, firmware, recovery |
| Shared configuration / dependency / schema | Expand to all consumers and critical journeys; upgrade/migration and rollback tests |
| Performance-sensitive path | Comparable version/data/hardware baseline, representative load, duration/latency/memory and agreed threshold |

Use a failing reproducer for a bug, then rerun after the fix. Include existing critical tests and the repository-required CI checks. An unrelated baseline failure still belongs in STATE; distinguish it with baseline evidence rather than silently dropping it. Document risk-based omissions, not only successes.

Each acceptance row needs: criterion, code status, required test level, real versus doubled dependencies, command/scenario, expected observable result, actual result, status, evidence path, source revision/fingerprint, environment identity and remaining limitation. Several rows can reference one evidence bundle. Manual hardware evidence also needs operator, UTC time, device/firmware and observed outputs/artifacts; the local helper does not certify a human observation.

The runner reports process results. Independently inspect:
- Is this the intended command in the intended environment? Did any tests actually execute, or were they skipped?
- Do assertions check the acceptance behavior, including persisted/remote side effects?
- Did a mock bypass the actual integration boundary? Which endpoint, service or hardware ran?
- Are logs complete enough? A truncated log requires a concise safe report or rerun with a focused reporter.
- Does code match HEAD + dirty fingerprint? Have dependencies, service state or target versions changed?

`check` is a local consistency gate, not an attestation system: a writer with file access can forge JSON and hashes. Agent review and direct reruns provide independence; high-assurance remote signed CI is outside this skill. No script can guarantee that every agent follows prose. Mark unavailable real services/hardware BLOCKED; mark checks that were simply not run NOT TESTED. Failure remains FAILED until fresh execution passes. A later blocked attempt does not erase historical failure.

No full feature acceptance from compilation, fixtures, mocks, screenshots, simulator-only testing or a subagent's success statement. Scope completion to what evidence proves.
