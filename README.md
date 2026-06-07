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
![Failure patterns: 24](https://img.shields.io/badge/Failure%20patterns-24-brightgreen.svg)

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
  N1 main-flow hardcodes Claude    M1 add a "non-zero → stop" hard check
  N2 compaction threshold mismatch    (edits the shared main flow — your call,
  N3 scenario count off by one         won't change automatically)
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

The skill auto-triggers on those phrasings and runs the full six-step audit.

---

## What It Catches

Four dimensions, **24 catalogued failure patterns**, each paired with a concrete *how-to-verify-on-disk* check:

| Dimension | What silently breaks here |
| :--- | :--- |
| **1 · System architecture** | Two disconnected execution paths wearing one name; docs that promise what the running path doesn't deliver; "drop a file and it works" that secretly needs a script edit. |
| **2 · Trigger reliability** | A discovery glob that misses subdirectories → empty registry; dead symlinks; a roster name that ≠ the dispatcher's name → lookup 404s; a forced `Skill(X)` pointing at an undiscoverable X. |
| **3 · Execution reliability** | State/recursion bugs; script-config seams that don't match; `2>/dev/null \|\| true` swallowing a critical failure; a loop cap that truncates silently; shared resources with no lock. |
| **4 · Declared vs wired** | Documented features the code never implements; a health-check that validates the wrong field (green ✓ ≠ runnable); empty dirs, hardcoded paths, a dependency that exists only as `.example`. |

Full pattern catalogue with per-pattern verification: [`references/failure-patterns.md`](references/failure-patterns.md).

---

## How It Works

Six steps. Each prints a visible `[harness-check] …` line so no step is silently skipped.

```
0 Discovery ─▶ 1 Inventory ─▶ 2 Scan (4 dims) ─▶ 3 Verify ─▶ 4 Report ─▶ 5 Self-check
```

**0. Discovery first** — the lifeline: can roles/skills/tools actually be found and invoked? Globs, symlinks, registry completeness, name consistency.
**1. Inventory** — read everything (config, rules, roster, role defs, scripts) before judging anything.
**2. Scan** — four dimensions against the 24-pattern catalogue.
**3. Verify** — the iron rule: *no verification, no finding.* Anything unverifiable on disk is downgraded to "suspected" or dropped.
**4. Report** — verdict, health scores, and code-layer evidence; then the **✅ Safe to fix now** / **🤔 Needs your decision** split, plus top failure scenarios.
**5. Self-check** — every file assessed, every finding verified, every `where` carries a `file:line`.

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
├── SKILL.md                          # methodology — the six-step flow
├── references/
│   ├── failure-patterns.md           # 24 patterns × how to verify each
│   ├── fix-risk-tiers.md             # 🟢/🟡/🔴 — risk of each fix
│   └── output-format.md              # the layered report shape
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
