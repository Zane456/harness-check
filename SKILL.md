---
name: harness-check
description: Agent-harness/framework structure auditor for multi-agent systems orchestrated via prompts, markdown, and scripts. ALWAYS invoke this skill when the user asks to 审查框架 / harness 体检 / 框架可靠性 / 框架有没有问题 / 检查我的框架 / 框架需要提升的点 / 大模型能不能稳定触发 / review my agent framework / harness review / audit my agent orchestration. Do not audit an agent harness directly — use this skill first. Does not review business logic or security/secret leaks.
---

# Harness Check — Agent Framework Structure Audit

You audit whether **the framework runs reliably as wired** — not business-code correctness, not security. Core stance: **does "the system the docs describe" equal "the system the code can actually run"?** A multi-agent harness's most common disease is these two quietly diverging.

A harness glues agents together with prompts, markdown, and scripts. One broken glue point — a trigger word, role discovery, a registry, a symlink, a script seam — silently kills a chain while the docs still claim full functionality. The audit surfaces what makes a harness "demo-works, production-fails".

This is a **generic** audit — assume no specific project layout, role names, or scripts. Establish the target root first (user-given path, or cwd).

## Five-step flow (each step MUST print one `[harness-check] …` line)

> A step with no visible output gets silently skipped. One line per step; a missing print = step not done.

### Step 0 · Discovery-mechanism reality check (the lifeline — verify first)
A harness is only alive if roles/skills/tools can actually be discovered and invoked. Verify up front:
- **Discovery glob coverage**: does a glob used to find roles/agents (e.g. single-level `*.md`) miss subdirectories → registry/roster comes back empty?
- **Symlink resolvability**: `find <root> -type l ! -exec test -e {} \; -print` to catch dead links.
- **Registry completeness**: any hardcoded member/role list ≟ the actual set on disk.
- **Naming consistency**: name in the roster ≟ name used by the dispatcher/launcher (mismatch → lookup fails).
- **Forced-trigger targets exist**: for any "you must use Skill/tool X" injected into a role, is X actually discoverable from that role's working dir or globally?

print: `[harness-check] discovery: glob=<ok/misses-subdir> dead-links=<n> registry=<full/missing X> naming=<ok/mismatch> forced-skill=<resolvable/N broken>`

### Step 1 · Mechanical inventory (read everything before judging; miss nothing)
ls/read first, judge later. Read all: root agent-config (CLAUDE.md/AGENTS.md/README), rules/charter, roster/org tables, every role/agent definition, templates, scripts, the orchestration/command/skill dirs, config, lock files. Produce an internal file checklist marking each [assessed / to-fix / no-change].

print: `[harness-check] inventory: read <N> files, coverage checklist built`

### Step 2 · Four-dimension scan
Scan each dimension; details and known failure patterns are in **references/failure-patterns.md**. Tag every finding with the dimension it hits:
1. **System architecture** — multiple disconnected execution paths, docs≟code, over-layering
2. **Trigger reliability** — trigger-word/routing clarity, missed/false triggers, discovery hits (from Step 0)
3. **Execution reliability** — orchestration/state flow/recursion, script-config seams, failure/timeout/interrupt recovery, concurrency, idempotency, silent truncation/error-swallowing
4. **Declared vs wired** — are declared features actually wired, paper features, whether the health-check validates the field that actually drives behavior

print: `[harness-check] scan: candidate findings=<N> (by dim 1/2/3/4=…)`

### Step 3 · On-disk verification (iron rule: no verification, no finding)
Every candidate finding must be verified in the files yourself — does the glob really match, is the symlink really dead, is the registry really short, is the field really inconsistent. Downgrade what you cannot verify to "suspected" or drop it. Never report inference as a conclusion.

print: `[harness-check] verify: confirmed=<N> downgraded/dropped=<M>`

### Step 4 · Output report
Present per **references/output-format.md** — a layered report written in **lesstoken style** (ultra-compressed; file:line / IDs / code / errors kept exact): verdict → health scores → a code-layer evidence block → a decision layer that speaks in effect + risk (not file:line, no filenames/constructs — name mechanisms by their role in the project), split into **✅ Safe to fix now** vs **🤔 Needs your decision** (each 🤔 item separates the mechanism — how it works now — from the consequence it causes, then options + rec). Actionable parts go last (terminal streaming → bottom is most visible). The bullets below are the substance that fills those layers.
- Findings ranked **XHigh / High / Medium / Low**, IDed X#/H#/M#/L#, each: what / where (file:line) / why / concrete fix, tagged with dimension; the decision layer points back via (Code layer: <ID>)
- **Fix recommendations in three risk tiers** (🟢 low-risk repair-only / 🟡 medium / 🔴 high), per `references/fix-risk-tiers.md`. Lead with 🟢 the user can apply safely; never present a 🔴 as one-click — it may break a currently-working path. Severity ≠ risk tier (an XHigh often has a 🟢 fix).
- Each 🤔 decision item separates the **mechanism** (how it works now) from the **consequence** it causes; when the real risk is a silent break (an action → break with no error), name it in the consequence line — no separate silent-break section
- **Self-assessment table**: score the 4 dimensions 1-5 + one line on coverage blind spots

print: `[harness-check] report: findings X#/H#/M#/L#=…, decision ✅=<n> 🤔=<n>`

### Step 5 · Self-check (if a box fails, go back and fill it)
- [ ] every file in the Step 1 checklist is marked [assessed/to-fix/no-change]
- [ ] every finding was verified on disk, none is pure inference
- [ ] every declared skill/role/feature was checked for whether it is wired
- [ ] every `where` gives file:line, no vagueness
- [ ] the self-assessment table honestly notes blind spots

print: `[harness-check] self-check: <all pass / N to refill>`

## Special cases
- **Framework not yet built / no orchestration script**: only trigger words and role definitions are auditable — say "execution-reliability dimension has insufficient data", don't manufacture findings.
- **Insufficient info**: unreadable files / un-runnable checks go into the blind spots, not inference.
- **Trade-offs needing the user's call**: list the options, don't decide unilaterally.

## Out of scope
Security/secret leaks, business-logic correctness, performance profiling — explicitly not checked; they distract from "can the framework run".

## Reference
- **references/failure-patterns.md** — per-dimension failure patterns + how to verify each on disk. Consult by dimension in Steps 2–3.
- **references/fix-risk-tiers.md** — how to classify each fix 🟢/🟡/🔴 by risk to working behavior. Use in Step 4.
- **references/output-format.md** — the layered report shape, written lesstoken/compressed: verdict → health scores → code-layer evidence → decision layer (✅ Safe to fix now / 🤔 Needs your decision) that speaks effect+risk, not code, with actionable parts last. Use in Step 4 to lay out the report.
