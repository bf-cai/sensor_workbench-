# Mandatory Engineering Rules

Apply these rules to every stage. They exist to improve correctness and maintainability, not to create paperwork.

## KISS and scope

- Implement the smallest complete solution satisfying the selected stage.
- Start from the actual problem and evidence, not a preferred framework.
- Prefer maintained libraries and Linux facilities over custom protocol stacks.
- Add abstractions only when two real implementations need the same boundary, or when a specified extension point is necessary.
- No empty scaffolding, generic plugin marketplaces, unused services, duplicate business logic, placeholder controls, or production mocks.
- Do not build features assigned to later stages.
- No unrelated refactoring. Fix underlying defects instead of hiding failures.
- Never fabricate device support, synchronization quality, performance, or test results.

## Reading files and conserving context

- **Never read or dump binary files unless their contents are essential to the current task.**
- Treat `.mcap`, `.pcap`, `.pcapng`, images, archives, executables, object files, compiled frontend bundles, wheels, databases, `.git/objects`, and dependency caches as opaque by default.
- Do not recursively print binary contents, `node_modules`, `.venv`, build outputs, or unrelated large directories into agent context.
- Start with filenames, metadata, sizes, documented schemas, and targeted text searches.
- When a binary is essential, use an appropriate format-aware parser or tool, inspect only the required records, and report what was examined.
- Do not hex-dump an entire capture or open every binary in a directory. Avoid inspecting secrets or unrelated user data.
- Binary fixtures may be read by automated tests when required to verify the implemented functionality; this is not permission for indiscriminate agent inspection.

## Naming and organization

- Python: `snake_case` modules/functions/variables; `PascalCase` classes; `UPPER_SNAKE_CASE` constants.
- TypeScript: `camelCase` values/functions; `PascalCase` types and React components.
- Use descriptive domain names. Avoid vague files such as `utils.py`, `helpers.ts`, `misc.py`, or numbered replacement modules.
- Organize code by responsibility or feature, following ARCHITECTURE.
- Keep functions focused, dependencies explicit, and imports acyclic.
- Tests should mirror the relevant source area and describe observable behavior.
- New top-level directories require a real architectural purpose.

## Documentation

- Maintain a useful root README with commands that actually work.
- Public Python APIs require accurate Google-style docstrings, including units, clock domains, side effects, and exceptions where relevant.
- Public TypeScript APIs and non-obvious logic require TSDoc/JSDoc.
- If C/C++ is justified later, use Doxygen for public interfaces and document ownership and threading.
- Comments explain **why**, not obvious syntax.
- Keep examples and configuration documentation synchronized with actual behavior.
- Do not copy product requirements into multiple files. SPEC is authoritative.

## Real formatters, linters, and tests

Stage 01 establishes these tools and reproducible commands. Every subsequent stage must run applicable checks.

**Python:** Ruff formatter, Ruff linter, mypy, pytest. Configure meaningful Ruff E/F/I/B/UP/RUF rules and public-API docstring checks; avoid blanket suppressions. Type-check core models and public boundaries strictly.

**TypeScript/React:** Prettier, ESLint with TypeScript rules, `tsc --noEmit` with strict checking, Vitest, and a production Vite build. Use Playwright for browser workflows beginning in Stage 07.

**Other:** ShellCheck and shfmt for maintained shell scripts; markdownlint-cli2 for Markdown; yamllint for YAML; actionlint if GitHub Actions are introduced. If C/C++ is added, configure clang-format, clang-tidy, and a real compiler/test build. If Rust is added, use rustfmt, clippy, and cargo test.

Required root targets:

- `make format-check`
- `make lint`
- `make typecheck`
- `make test`
- `make build`
- `make quality`

`make quality` must execute the real applicable checks, not echo success. A skip is allowed only when no applicable files exist, and must be visible. Do not weaken rules, exclude application directories, or modify tests to manufacture a pass.

Use Python `pyproject.toml` and committed `uv.lock`; frontend `package.json` and committed `package-lock.json`. Document and verify dependency bootstrap commands.

## Tests and acceptance

- Test working behavior and meaningful failures, not just imports.
- Keep deterministic simulation tests separate from physical hardware tests.
- Include clock resets, stale data, missing timestamps, malformed inputs, permissions, and disconnections where applicable.
- Test cleanup/cancellation when introducing background work or subprocesses.
- Record exact commands, exit codes, and outcomes in each handoff.
- Never mark `NOT_RUN` or `UNVERIFIED_HARDWARE` as `PASS`.
- If hardware is unavailable, verify with fixtures and clearly record what remains physically unverified.
- No stage advances while a mandatory software acceptance test fails.

## Timing correctness

- Preserve raw timestamps, units, clock domains, and sample-time semantics.
- Keep measurement, transmit, kernel receive, userspace receive, and display times separate.
- Use integer nanoseconds where representable; never float-valued epoch nanoseconds.
- Use monotonic time for durations and record boot identity for host monotonic timestamps.
- Distinguish UTC, TAI, GPS, PTP, device-local, and monotonic time scales.
- Unknown uncertainty means unknown, not zero.
- Synchronization flags, network arrival lag, clock offset, and physical measurement alignment are distinct.
- Raw evidence is immutable; corrections are versioned derived data.

## Security and reliability

- Listen on loopback by default. Remote LAN access requires explicit enablement and authentication.
- Read-only device inspection is the default.
- Never automatically disable NTP, alter system time, change network routes, reconfigure CAN, or start a conflicting PTP daemon.
- Privileged operations must be narrowly scoped, authorized, auditable, and cleaned up.
- Never offer arbitrary browser-to-shell execution.
- Bound queues, storage, memory, and live chart buffers; report drops and stale sources.
- Acquisition and recording must continue independently of browser connections.
- Do not overwrite user configuration or recordings silently.

## Stage handoff

Before implementation, set STATUS to `in_progress`.

After implementation, write `handoffs/NN.md` with:

1. Outcome and working deliverables.
2. Important files and changed public contracts.
3. Exact checks run and PASS/FAIL/NOT_RUN results.
4. Physical hardware tested versus simulation/fixtures.
5. Known defects, limitations, and blockers.
6. Commands and facts the next agent needs.

Then update STATUS. If blocked, retain the same stage. Stop after one stage.
