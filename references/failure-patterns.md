# Known Agent-Harness Failure Patterns

Per-dimension high-frequency failure patterns + **how to verify**. This is the reference table for the scan (SKILL Step 2) and on-disk verification (Step 3) — not rigid rules. A hit must land on a concrete `file:line`; downgrade anything you cannot verify. Patterns are generic across harnesses; the file/identifier names below are illustrative, not assumed to exist.

---

## 1. System architecture

- **Multiple disconnected execution paths**: the framework has two ways to run the same work (e.g. a manually-launched path vs an orchestration-script path) that run independently with inconsistent semantics, yet the docs describe them as one set of promises. Result: one path does not get the isolation/cost/routing the other advertises.
  - Verify: grep the entry point of each path; check whether the orchestration path actually invokes the advertised mechanism. If not, they are two different systems wearing one name.
- **Docs = two companies**: capabilities described in the README/rules do not hold on the code path that actually executes.
  - Verify: take one typical task, walk the path that will really run, check each advertised point lands.
- **Over-layering / adding a layer needs a code edit**: hardcoded constants (e.g. a role-name array) prop up "extensibility", but adding a role/group requires editing a script — contradicting a "drop a file and it works" claim.
  - Verify: check whether adding one role requires editing a `.js`/`.sh`; if yes, the extensibility is fake.

## 2. Trigger reliability

- **Orchestration registry misses a member**: a hardcoded member array (a roster/stage constant) omits a role/group → that branch is never reached.
  - Verify: diff the hardcoded array against the actual set of roles/groups on disk.
- **Non-recursive discovery glob → empty registry**: a command/script uses a single-level glob (e.g. `agents/*.md`) but definitions live in subdirectories → matches zero → the downstream registry is empty → the whole orchestration goes silent.
  - Verify: actually run that glob at the project root and see whether it matches files.
- **Forced `Skill/tool X` points at an undiscoverable target**: an instruction injects "first you must use X" but X is not discoverable from that role's working dir nor globally → trigger fails / the model runs bare.
  - Verify: for each forced skill/tool, list the role's discovery dir + the global dir, confirm X resolves.
- **Discovery dir empty or missing links**: the platform discovers resources per working-dir, but the dir holds only a placeholder → all that role's per-project resources are inert.
  - Verify: list each role's discovery dir; an empty/placeholder-only dir = broken.
- **Dead links**: a resource a doc claims is "installed" points (via symlink/path) to a target that does not exist.
  - Verify: `find <root> -type l ! -exec test -e {} \; -print`, or resolve each referenced path.
- **Naming mismatch → lookup fails**: the role name in the roster ≠ the name used by the dispatcher/launcher → upstream lookup-by-name 404s.
  - Verify: cross-grep the same role's spelling across roster vs launch config vs scripts.
- **Decision rules overloaded → trigger dilution**: the always-on config's rules for "what to delegate / what to do myself" cross-reference heavily and use subjective, non-machine-decidable thresholds → the model re-derives every turn, easily over-delegating or under-triggering.
  - Verify: read the rule block, ask "can a model decide this mechanically"; if not, it drifts.
- **Routing responsibility overlap**: multiple roles/skills have semantically overlapping trigger conditions, disambiguated only by long prose caveats with no structured "do not use for…" boundary.
  - Verify: check whether each role has a scannable negative boundary, or relies on prose to separate.

## 3. Execution reliability

- **State-machine / recursion correctness**: are the orchestration recursion's termination/dispatch conditions correct (leaf detection, child lookup)?
  - Verify: read the recursion/child-lookup function, walk it against the registry data.
- **Broken script-config seam**: the params/paths a script reads do not match what the config/launch spec provides.
  - Verify: grep the script's variable sources, check the config/env actually supplies them.
- **Incomplete failure/timeout/interrupt recovery**: timeout detection covers only some exit codes; failure reporting relies on the model's diligence; no checkpoint.
  - Verify: read the timeout/retry branch, check exit-code coverage and "can it resume after interrupt".
- **Shared-resource concurrency with no lock**: multiple roles share a single port/session/credential, relying on a doc convention "run serially" rather than a lock/queue.
  - Verify: grep how many roles reference the same resource, check for a locking mechanism.
- **Cross-run state pollution**: a long-lived session/workspace (a single REPL/kernel/app session held by an MCP server or daemon, reused across runs) is never reset, and one run's leftovers — variables shadowing functions, temp files, dirty caches — break later runs. The failure masquerades as a broken carrier or environment flaw, and the docs' "each run = fresh session" assumption silently fails.
  - Verify: read the run-start path for an explicit reset (close-all / clear / assert-clean baseline). To triage a suspected case, run the control experiment: same environment, a sibling carrier, full session cleanup, then re-run — if cleanup alone makes it pass, the root cause is pollution, not the carrier/environment.
- **Idempotency**: are ledger/state writes append-only/atomic; will a re-run duplicate or corrupt?
  - Verify: check whether writes use append+lock or overwrite.
- **Silent truncation**: a loop cap (e.g. a max-steps limit) hits the ceiling and just breaks without flagging "incomplete"; upstream cannot tell completion from being cut off.
  - Verify: read the loop-cap branch, check whether hitting the ceiling reports explicitly.
- **Silent error swallowing**: a critical step uses `2>/dev/null || true`, swallowing failures (e.g. a ledger write fails with no warning).
  - Verify: grep `2>/dev/null`, `|| true`; see whether the swallowed step is critical.
- **Double-execution bug**: the same action is invoked twice by a script, the second overwriting the first's output or carrying an unrelated hardcoded prompt.
  - Verify: read the script branches, see whether the same output target is redirected more than once.

## 4. Declared vs wired (paper features)

- **Declared but not wired**: a feature the rules/templates/roster claim has no corresponding implementation (e.g. an "auto-remediate" that only detects and never acts; a "mandatory QC gate" that half the roles have no agent for).
  - Verify: for each declared feature, grep the implementation; only-scan/only-append with no action = paper.
- **Health-check validates the wrong field**: the check script validates a declarative field (e.g. a frontmatter `model`) while the field that actually drives behavior is something else (an env var / cwd / skill discoverability) → a green check ≠ actually runnable.
  - Verify: read the check script's assertions ≟ the fields that actually affect runtime.
- **Empty dir / empty config**: a placeholder dir / empty json treated as a ready capability.
  - Verify: `find -empty`, `wc -c` on config files.
- **Hardcoded paths**: scripts/config hardcode absolute paths or leftover residue from another project (e.g. unrelated permissions in a local settings file).
  - Verify: grep for absolute paths, cross-project names.
- **Missing dependency**: a declared MCP/tool/flow-script that exists only as a `.example` or not at all.
  - Verify: cross-check declared dependencies against actual file existence.
