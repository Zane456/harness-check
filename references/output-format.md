# Output Format — Layered Audit Report

How Step 4 presents the audit. Two facts drive the shape:

1. Reader owns the harness, rarely reads its code (an LLM wrote it). file:line / glob /
   symlink detail is useless to them. They act on: after this fix, does behavior change? is it
   risky? does it touch anything that already works?
2. Output streams in a terminal — eyes land on the **bottom**. Low-value audit trail sits in
   the middle (scrolled past); actionable parts go last.

## Write the whole report in lesstoken style

Ultra-compressed. Drop filler (其实/就是/基本上/然后 · just/really/basically/actually),
pleasantries, hedging. Fragments OK. Short word over long. Arrows for causality (X → Y). One
word when one word enough. Pattern: `[thing] [action] [reason]. [next].` Aim: half the prose,
same facts.

Exact-keep — never compress: file:line, IDs (X#/H#/M#/L#), code blocks, error strings, field /
column / schema names, dimension tags.

Match the user's reply language.

Auto-clarity exception (drop compression here): irreversible-fix warnings and any multi-step
fix sequence where fragment order could be misread — write those in normal prose.

## Section order (top → bottom)

1. **Verdict** — one line: is the main/everyday path healthy, which 1–2 buckets the problems
   fall in.
2. **Health scores** — the 4-dimension table (1–5) + a one-line **Blind spots** note.
3. **Code layer** — the evidence/audit trail. Header is exactly "Code layer" (no
   parenthetical). Never drop it — it is why the verdict is trustworthy.
4. **✅ Safe to fix now** — pure fixes.
5. **🤔 Needs your decision** — judgment calls.
6. **Closing question** — one concrete action question. Last line = most visible.

No standalone "failure scenarios" section. The top trigger- + top execution-reliability
silent-break scenarios fold **into** the §4/§5 item they belong to — see Decision layer below.

## Code layer — severity, IDs, format

Findings ranked **XHigh / High / Medium / Low**, grouped under those headers. Each gets a
stable ID = severity initial + number: **X# / H# / M# / L#** (Low = L; M is Medium). This ID is
the cross-reference anchor the decision layer points to.

The fix-risk circle 🟢/🟡/🔴 goes **first**, then ID, plain name, dimension; sub-lines below,
lesstoken (facts kept, prose cut):

    🟡 M1 Script failure goes unchecked — dim3 execution
    where: <file:line>
    why: <what silently breaks — compressed>
    mitigation: <if any>
    fix: <concrete change>

Circles: 🟢 repair-only/additive · 🟡 touches working logic · 🔴 design/architecture change.

## Decision layer

Re-frame every confirmed finding into two buckets by **whether the user must decide
anything**. Each item: plain name + back-pointer **(Code layer: <ID>)**. No file:line, no
jargon — speak in behavior. Compressed.

### ✅ Safe to fix now
Pure fixes (🟢): something meant to work is broken/unwired; fixing only restores it, logic
unchanged, nothing working regresses.

    before: <bad effect the user actually sees>
    after: <normal effect once fixed>
    risk: low; only touches the already-broken path

### 🤔 Needs your decision
Judgment calls (🟡/🔴): a design fork, or a change touching a path that currently runs.

    current: <the gap, in plain effect terms>  (not a bug — a trade-off / check upgrade)
    decision: <the explicit either/or>
    rec + blast radius: <your pick, what it touches, "won't change automatically">

### Fold the two silent-break scenarios in here
Don't trail them as their own section. Pick the top **trigger-reliability** scenario and the
top **execution-reliability** scenario; attach each as one line **inside** the §4/§5 item it
maps to:

    silent-break: when you do X, Y quietly breaks (no error)

It lands in whichever bucket its owning finding sits in (a 🟡/🔴 finding → its 🤔 item; a 🟢
finding → its ✅ item). If a scenario has no matching item, append the line under the closest
finding — never re-open a standalone section.

## Closing question
One line: offer to apply the ✅ Safe-to-fix items now, leave the 🤔 decision items.

## Mapping
- 🟢 → Safe to fix now　·　🟡 / 🔴 → Needs your decision
- Severity (XHigh/High/Medium/Low) lives in the Code layer; the bucket lives in the decision
  layer. Independent — an XHigh with a 🟢 fix is a "Safe to fix now" item.
