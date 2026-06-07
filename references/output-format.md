# Output Format — Layered Audit Report

How Step 4 presents the audit. Two facts drive the shape:

1. The reader owns the harness but rarely reads its code (an LLM wrote it). file:line /
   glob / symlink detail is useless to them. They act on: after this fix, does behavior
   change? is it risky? does it touch anything that already works?
2. Output streams in a terminal — eyes land on the **bottom**. So the low-value audit
   trail sits in the middle (scrolled past); the actionable parts go last.

Match the user's reply language.

## Section order (top → bottom)

1. **Verdict** — one line: is the everyday/main path healthy, which 1–2 buckets the
   problems fall in.
2. **Health scores** — the 4-dimension table (1–5) + a one-line **Blind spots** note.
3. **Code layer** — the evidence/audit trail. Header is exactly "Code layer" (no
   parenthetical). Never drop it — it is why the verdict is trustworthy.
4. **Safe to fix now** — pure fixes.
5. **Needs your decision** — judgment calls.
6. **Two failure scenarios** — top trigger + top execution scenario.
7. **Closing question** — one concrete action question. Last line = most visible.

## Code layer — severity, IDs, format

Findings ranked **XHigh / High / Medium / Low**, grouped under those headers. Each gets
a stable ID = severity initial + number: **X# / H# / M# / L#** (Low = L; M is Medium).
This ID is the cross-reference anchor the decision layer points to.

The fix-risk circle 🟢/🟡/🔴 goes **first**, then ID, plain name, dimension; sub-lines below:

    🟡 M1 Script failure goes unchecked — dim3 execution reliability
    where: <file:line>
    why: <what silently breaks>
    mitigation: <if any>
    fix: <concrete change>

Circles: 🟢 repair-only/additive · 🟡 touches working logic · 🔴 design/architecture change.

## Decision layer

Re-frame every confirmed finding into two buckets by **whether the user must decide
anything**. Each item: plain name + back-pointer **(Code layer: <ID>)**. No file:line, no
jargon — speak in behavior.

### ✅ Safe to fix now
Pure fixes (🟢): something meant to work is broken/unwired; fixing only restores it,
logic unchanged, nothing working regresses.

    before: <bad effect the user actually sees>
    after: <normal effect once fixed>
    risk/blast radius: low; only touches the already-broken path

### 🤔 Needs your decision
Judgment calls (🟡/🔴): a design fork, or a change touching a path that currently runs.

    current: <the gap, in plain effect terms>  (it's not a bug — a trade-off / check upgrade)
    your decision: <the explicit either/or>
    recommendation + blast radius: <your pick, what it touches, "won't change automatically">

## Two failure scenarios
Top trigger-reliability + top execution-reliability scenario, each a concrete
"when you do X, Y silently breaks".

## Closing question
One line: offer to apply the Safe-to-fix items now, leave the decision items.

## Mapping
- 🟢 → Safe to fix now　·　🟡 / 🔴 → Needs your decision
- Severity (XHigh/High/Medium/Low) lives in the Code layer; the bucket lives in the
  decision layer. Independent — an XHigh with a 🟢 fix is a "Safe to fix now" item.
