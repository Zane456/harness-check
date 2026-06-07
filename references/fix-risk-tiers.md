# Fix Risk Tiers

When recommending fixes, classify each by **how likely it is to break a currently-working part of the framework** — not by how important the bug is. The user's fear is that a fix damages a working system. So a broken-but-isolated bug with a safe fix should be surfaced as "apply now", while a fix that rewires working logic must be staged carefully.

## Classifying signals (ask in order)

1. **Repair-only vs mutative**: does the fix only restore a path that is *currently broken/dead* (a dead symlink, an empty registry, a glob matching nothing), or does it change a path that *currently works*? Repair-only is lower risk — there is no working behavior to regress.
2. **Additive vs in-place**: adding a file/symlink/missing list member/warning line is lower risk than editing existing control flow.
3. **Reversibility**: can it be undone in one step (rm the symlink, revert one line)? One-step-reversible is lower risk.
4. **Blast radius**: does it affect one role/file, or shared orchestration every task flows through? Wider = higher.

## The three tiers

### 🟢 Low-risk (safe to apply now; repair-only, additive, one-step reversible)
Restores a broken/dead path and touches no working behavior.
- Add a missing symlink so a forced skill/tool resolves
- Remove a dead symlink (it resolves to nothing today → removing it changes no working behavior)
- Make a discovery glob recursive when it currently matches zero files
- Add a missing member to a hardcoded registry that omits one (the omitted branch is dead today)
- Add a warning/marker on a silent-truncation or silent-error path (pure addition)
- Fix a name mismatch where the current name 404s
Present as "safe to apply now"; still verify each on disk first.

### 🟡 Medium-risk (touches working logic; apply, then verify)
Modifies a path that currently runs, contained blast radius.
- Add a lock/serialization to a shared resource (changes timing of working flows)
- Change timeout / exit-code / recovery handling
- Refactor a hardcoded list into dynamic discovery (behavior should match, but must be checked)
Pair each with a concrete post-fix check ("rerun X, confirm Y unchanged").

### 🔴 High-risk (could change architecture or break working flows; propose, do not auto-apply)
Rewires shared structure or resolves a design trade-off.
- Unify two divergent execution paths into one
- Restructure orchestration recursion / state model
- Rewrite always-on decision rules
For these: describe the change + blast radius, list what could break, recommend staging (back up first, change one path, keep the old one reachable), and ask the user to decide. Never present as a one-click fix.

## Reporting rule

Group fixes under the three tiers, 🟢 first. A finding's **severity** (XHigh/High/Medium/Low) and its fix's **risk tier** are independent — an XHigh can have a 🟢 low-risk fix (e.g. repairing an empty registry), and that is exactly the kind to surface first. State reversibility and blast radius for every 🟡 and 🔴.
