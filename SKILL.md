---
name: harness-check
description: Agent harness/多代理框架结构体检。用户点名「harness 体检」「审查框架」「框架可靠性」时调用；不审业务逻辑与安全。
---

# Harness Check — Agent Framework Structure Audit

You audit whether **the framework runs reliably as wired**. Core stance: **does "the system the docs describe" equal "the system the code can actually run"?**

One broken glue point (a trigger, a registry, a symlink, a script seam) silently kills a chain while docs claim full functionality.

Generic audit — assume no specific layout, role names, or scripts. Establish the target root first (user path or cwd).

## Flow (each step MUST print one `[harness-check] …` line)

> No visible output = silently skipped; a missing print = step not done.
> **Self-review flag**: this session already edited the audited harness → prefix every print with `[self-review]`, and a fresh sub-agent blind re-audit (target root, NO expected findings) MUST run before declaring done; print `[harness-check] self-review re-check: <agent> → <verdict>`. Cannot run → mark **unverified**, never silently.

### Step 0 · Discovery reality check (the lifeline)
**Run this skill's `scripts/check_discovery.py <root>` first** — dead symlinks, glob coverage, name inventory. Cite its lines — script lines = leads, YOU verify (can't run → by hand, say so; exit 2 = bad root, fix the root, don't fall back). Then judge:
- **Registry completeness** — hardcoded member/role lists ≟ the set on disk (vs its inventory).
- **Naming consistency** — roster ≟ dispatcher/launcher name (mismatch → lookup fails).
- **Forced-trigger targets** — every injected "must use Skill/tool X" resolves from the role's working dir or globally.

print: `[harness-check] discovery: glob=<ok/misses/skill-pkg/none> dead-links=<n> registry=<full/missing N> naming=<ok/mismatch> forced=<ok/N broken>`

### Step 1 · Mechanical inventory (miss nothing)
ls/read first, judge later — root agent-config (CLAUDE.md/AGENTS.md/README), rules/charter, rosters, every role definition, templates, scripts, orchestration/command/skill dirs, configs, locks. Checklist every file [assessed / to-fix / no-change]; reconcile the count against check-discovery's `files-walked` line, name what you skipped.

print: `[harness-check] inventory: read <N>/<files-walked>, marks a/f/n=<a>/<f>/<n>`

### Step 2 · Four-dimension scan
**Run `scripts/check_mechanical.py <root>`** — the mechanical slice of dims 3/4 (swallow/empty/hardcoded/example-only). It reports hits, YOU convict — a `|| true` can be legitimate (can't run → by hand, say so). Then walk EVERY pattern in [references/failure-patterns.md](references/failure-patterns.md); tag each finding with its dimension:
1. **System architecture** — disconnected execution paths, docs≟code, over-layering
2. **Trigger reliability** — routing clarity, missed/false triggers, discovery hits (Step 0)
3. **Execution reliability** — state flow/recursion, script-config seams, recovery, concurrency, idempotency, silent truncation/swallowing
4. **Declared vs wired** — paper features, health-check validating the wrong field

print: `[harness-check] scan: patterns=<p>/<total> mech-hits=<H> findings=<N> (dim 1/2/3/4=…)`

### Step 2.5 · End-to-end walkthrough (positive once, negative always)
Per [references/walkthrough.md](references/walkthrough.md). Positive: walk ONE typical task through the real chain on disk — trigger → dispatch → execution → reporting; an unconnected link = candidate finding; no orchestration → skip positive, say so. Negative ALWAYS: judge 1–2 should-NOT-trigger tasks against the always-on rules; false-fire = dim2 finding.

print: `[harness-check] walkthrough: <"task" links ok=<n> broken=<m> | positive=skipped (no orchestration)>; negative false-fire=<k>/<j>`

### Step 3 · On-disk verification (no verification, no finding)
Verify every candidate finding in the files yourself — glob really matches? field really inconsistent? Unverifiable → downgrade to "suspected" or drop; never report inference as conclusion.

print: `[harness-check] verify: confirmed=<N> downgraded/dropped=<M>`

### Step 4 · Output report
Present per [references/output-format.md](references/output-format.md) — layered, lesstoken: verdict → health scores (4 dims 1–5 + blind spots) → Code layer (ranked **XHigh/High/Medium/Low**, IDs X#/H#/M#/L#, file:line, dim tag) → decision layer **✅ Safe to fix now** vs **🤔 Needs your decision** (mechanism vs consequence, back-pointer (Code layer: <ID>)). Risk tiers 🟢/🟡/🔴 per [references/fix-risk-tiers.md](references/fix-risk-tiers.md); severity ≠ risk tier. Same defect from two dims = ONE finding, both tags.

print: `[harness-check] report: fmt-ref✓ findings X#/H#/M#/L#=…, decision ✅=<n> 🤔=<n>`

### Step 5 · Self-check (a failed box → go refill)
- [ ] every Step 1 checklist file is marked
- [ ] every finding verified on disk with file:line, none pure inference
- [ ] every declared skill/role/feature checked for being wired
- [ ] scripts ran and cited (or fallback announced); walkthrough ran or skip printed
- [ ] every step's print line was emitted
- [ ] the health-scores table honestly notes blind spots

print: `[harness-check] self-check: <✓/✗ per box → all pass | refill #k>`

### Step 6 · Apply (only on the user's explicit go)
**Never** edit without confirmation. Default-apply 🟢 only; each 🟡/🔴 needs its own decision. Close the loop per [references/fix-risk-tiers.md](references/fix-risk-tiers.md) §Apply protocol — re-run both scripts + re-verify each fix on disk; skipped re-check = unverified.

print: `[harness-check] applied: <n> fixes; re-run discovery=<…> mechanical=<…>`

## Special cases
- **No orchestration yet**: only triggers and role definitions auditable — say "dim3 insufficient data", don't manufacture findings.
- **Insufficient info**: unreadable/un-runnable → blind spots, not inference.
- **User-call trade-offs**: list options, don't decide unilaterally.

## Out of scope
Security/secret leaks, business-logic correctness, performance profiling — explicitly not checked.
