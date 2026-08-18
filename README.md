[English](README.md) | [简体中文](README.zh-CN.md)

<div align="center">

# harness-check

<p align="center">
  <img src="assets/hero.png" alt="harness-check — agent harness structure auditor for Claude Code" width="640" />
</p>

> *"Docs describe one system. Code runs another. Find the gap before your users do."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-blueviolet.svg)](https://claude.com/claude-code)
![Type: Agent Skill](https://img.shields.io/badge/Type-Agent%20Skill-blue.svg)
![Failure patterns: 25](https://img.shields.io/badge/Failure%20patterns-25-brightgreen.svg)

<br>

**A structure auditor for multi-agent harnesses — does the system your docs describe equal the system your code can actually run?**

<br>

harness-check audits agent frameworks wired together from prompts, Markdown, and scripts. It hunts the *glue* — a trigger word, role discovery, a registry, a symlink, a script seam. Where one quiet break kills a whole chain while the docs still claim full functionality. It verifies every finding against your real files (no guessing), and reports findings as plain-language before/after comparisons — not a wall of line numbers.

<br>

[See Demo](#demo) · [Install](#install) · [What It Catches](#what-it-catches) · [How It Works](#how-it-works) · [Why It's Different](#why-its-different)

</div>

---

## Demo

A real audit run, condensed. You ask in plain language; it answers in a layered report:

```text
❯ "review my agent framework"

VERDICT — the everyday main path (Claude running the test loop) is healthy and
fully wired: preflight green, zero dead links, every script arg lines up, locks
correct. No XHigh/High — a few doc-drift items + 1 "relies on the model paying
attention" robustness note.

📊 Health scores      architecture 5 · trigger 4 · execution 4 · declared-vs-wired 4

CODE LAYER  (the audit trail, skippable)
  🟡 M1  Script failure goes unchecked — dim3 execution reliability
         where: testing/test-runner.md:177-199
         why:   the pseudocode never checks state-script exit codes → a failed
                status flip gets treated as success and the loop walks on
         fix:   add Supervisor rule "any state script non-zero → stop + report"

✅ SAFE TO FIX NOW              🤔 NEEDS YOUR DECISION
  L1 main-flow hardcodes Claude    M1 add a "non-zero → stop" hard check
  L2 compaction threshold mismatch    (edits the shared main flow — your call,
  L3 scenario count off by one         won't change automatically)
```

It doesn't bury you in line numbers. It tells you **what silently breaks, what's safe to fix right now, and what needs your call** — because when an LLM wrote the harness, you need a second pair of eyes.

---

## Install

It's a [Claude Code](https://claude.com/claude-code) skill — drop it in your skills directory:

```bash
git clone https://github.com/Zane456/harness-check.git ~/.claude/skills/harness-check
```

Then just ask, in any wording:

```text
review my agent framework   ·   harness review   ·   审查我的框架   ·   harness 体检
```

The skill auto-triggers on those phrasings and runs the full eight-step audit.

---

## What It Catches

Four dimensions, **25 catalogued failure patterns**, each paired with a concrete *how-to-verify-on-disk* check:

| Dimension | What silently breaks here |
| :--- | :--- |
| **1 · System architecture** | Two disconnected execution paths wearing one name; docs that promise what the running path doesn't deliver; "drop a file and it works" that secretly needs a script edit. |
| **2 · Trigger reliability** | A discovery glob that misses subdirectories → empty registry; dead symlinks; a roster name that ≠ the dispatcher's name → lookup 404s; a forced `Skill(X)` pointing at an undiscoverable X. |
| **3 · Execution reliability** | State/recursion bugs; script-config seams that don't match; `2>/dev/null \|\| true` swallowing a critical failure; a loop cap that truncates silently; shared resources with no lock. |
| **4 · Declared vs wired** | Documented features the code never implements; a health-check that validates the wrong field (green ✓ ≠ runnable); empty dirs, hardcoded paths, a dependency that exists only as `.example`. |

Full pattern catalogue with per-pattern verification: [`references/failure-patterns.md`](references/failure-patterns.md).

---

## How It Works

Eight steps. Each prints a visible `[harness-check] …` line so no step is silently skipped.

```
0 Discovery ─▶ 1 Inventory ─▶ 2 Scan (4 dims) ─▶ 2.5 Walkthrough ─▶ 3 Verify ─▶ 4 Report ─▶ 5 Self-check ─▶ 6 Apply
```

**0. Discovery first** — the lifeline: can roles/skills/tools actually be found and invoked? Globs, symlinks, registry completeness, name consistency — the mechanical half measured by `scripts/check_discovery.py`.
**1. Inventory** — read everything (config, rules, roster, role defs, scripts) before judging anything; the read count is reconciled against the script's file total.
**2. Scan** — four dimensions against the 25-pattern catalogue; the greppable slice (error swallowing, empty configs, hardcoded paths, example-only deps) measured by `scripts/check_mechanical.py`, legitimacy judged in context.
**2.5. Walkthrough** — one typical task walked end-to-end through the real chain (trigger → dispatch → execution → reporting), plus 1–2 should-NOT-trigger tasks to catch over-broad routing.
**3. Verify** — the iron rule: *no verification, no finding.* Anything unverifiable on disk is downgraded to "suspected" or dropped.
**4. Report** — verdict, health scores, and code-layer evidence; then the **✅ Safe to fix now** / **🤔 Needs your decision** split, with the top trigger- and execution-reliability silent-break scenarios folded into those items. Written compact (lesstoken), behavior-first.
**5. Self-check** — every file assessed, every finding verified, every `where` carries a `file:line`.
**6. Apply** — only on your explicit go: 🟢 fixes by default, each 🟡/🔴 decided per item, then both scripts re-run to prove each fix landed.

---

## Why It's Different

| | Most "reviews" | harness-check |
| :--- | :--- | :--- |
| **Target** | business-logic correctness and security | whether the framework *runs as wired* |
| **Evidence** | plausible inference | verified on your real files, or dropped |
| **Fix advice** | "here's the bug" | severity **and** fix-risk (🟢 safe now / 🟡 use caution / 🔴 may break a running path) |
| **Report voice** | file:line everywhere | before/after behavior — what changes, how risky |

**Out of scope (on purpose):** secret leaks, business-logic correctness, performance profiling — they distract from the one question: *can the framework run?*

---

## Repository Structure

```
harness-check/
├── SKILL.md                          # methodology — the eight-step flow
├── references/
│   ├── failure-patterns.md           # 25 patterns × how to verify each
│   ├── fix-risk-tiers.md             # 🟢/🟡/🔴 — risk of each fix + apply protocol
│   ├── output-format.md              # the layered report shape
│   └── walkthrough.md                # end-to-end walkthrough procedure
├── scripts/
│   ├── check_discovery.py            # mechanical: symlinks, glob coverage, name inventory
│   └── check_mechanical.py           # mechanical: swallow/empty/hardcoded/example-only
├── assets/hero.png
└── README.md
```

---

<div align="center">

> *Docs describe one system. Code runs another.*
> *harness-check finds where they split.*

<br>

**Zane456**

| Platform | Link |
| :--- | :--- |
| 🐙 GitHub | [@Zane456](https://github.com/Zane456) |

<br>

⭐ If harness-check saves you from a silent break, consider starring it.

MIT License © [Zane456](https://github.com/Zane456)

</div>
