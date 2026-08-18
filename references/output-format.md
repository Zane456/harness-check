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

Exact-keep — never compress, never translate: file:line, IDs (X#/H#/M#/L#), code blocks, error
strings, field / column / schema names from the audited project, dimension tags (`dim3`).

Match the user's reply language — and commit to it, no half-mixing. When that language is
Chinese, the report is **basically all Chinese**: prose, section headers, AND the field labels
in the templates below all get translated. Don't strew English scaffolding words through Chinese
sentences. Target mapping (use these, adapt as needed):

    before→修复前 · after→修复后 · risk→风险 · current→现状 · consequence→后果 · decision→解决方案 · fix→改法
    where→位置 · why→原因 · mitigation→缓解 · rec + blast radius→建议

The only things that stay non-Chinese are: the Exact-keep tokens above; **proper nouns** —
project names / codenames, role names, tool names — which keep their original form (a project
codenamed `nightwatch` stays `nightwatch`, don't translate it); and the language-neutral emoji
(🟢/🟡/🔴 · ✅/🤔). Everything else follows the reply language.

Auto-clarity exception (drop compression here): irreversible-fix warnings and any multi-step
fix sequence where fragment order could be misread — write those in normal prose.

## Section order (top → bottom)

1. **Verdict** — one line: is the main/everyday path healthy, which 1–2 buckets the problems
   fall in.
2. **Health scores** — the 4-dimension table (1–5) + a one-line **Blind spots** note.
   Anchor the scale (same anchors every run): **5** = verified clean · **4** = minor findings,
   no silent break · **3** = runs, but carries a silent-break risk · **2** = a chain is broken ·
   **1** = the dimension's main path is dead.
3. **Code layer** — the evidence/audit trail. Header is exactly **Code layer** (or **代码层**
   in a Chinese report), no parenthetical. Never drop it — it is why the verdict is trustworthy.
4. **✅ Safe to fix now** — pure fixes.
5. **🤔 Needs your decision** — judgment calls.
6. **Closing question** — one concrete action question. Last line = most visible.

## Code layer — severity, IDs, format

Findings ranked **XHigh / High / Medium / Low**, grouped under those headers. Each gets a
stable ID = severity initial + number: **X# / H# / M# / L#** (Low = L; M is Medium). This ID is
the cross-reference anchor the decision layer points to.

Severity rubric (place by asking "what happens on the next real run?"):
- **XHigh** — a main/everyday path is dead or silently produces wrong results
- **High** — a whole chain/role/feature silently broken, main path still works
- **Medium** — degraded or latent: breaks under a plausible condition (concurrency, re-run, edge input)
- **Low** — cosmetic/doc drift; no behavior change today

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
anything**. Each item: plain name + back-pointer **(Code layer: <ID>)**. Compressed.

**Altitude rule — this layer's entire reason to exist.** The reader owns the harness but
doesn't read its code. The Code layer already holds every file:line, filename, and construct;
this layer is where you say *what changes for them and why they'd care*. So:

- **No code artifacts here.** No filenames (`config.md`, `registry.json`, `index.md`), no
  constructs (docstring, frontmatter, schema columns, section numbers §X, field names like
  `status:`/`owner:`), no internal jargon. All of it stays in the Code layer, reachable via the
  (Code layer: <ID>) pointer. The moment you type a `.md` or a construct name, you've fallen
  back into the code layer — rewrite the line.
- **Name a mechanism by its role, not its file.** When a moving part must be mentioned, say the
  *job it does in the harness* in one clause — "the check that's meant to flag a dead role link",
  "the registry that lists your agents" — never the file it lives in or the construct it's made
  of.
- **Speak macro effect.** before/after/current = what the user actually experiences, gains, or
  loses in their workflow. NOT "three places disagree" / "A says X, B says Y" — that internal
  mismatch is the *evidence*, and it belongs in the Code layer. Here, say what the mismatch
  *costs them*: what silently goes unguarded, what they'll never be warned about.

One worked rewrite — same finding, wrong altitude → right altitude:

    ✗ code-layer leak (what NOT to write here):
      current: the role-discovery glob is single-level `*.md` so nested role files are missed;
               the registry hardcodes 5 members but disk has 8 → three places disagree
    ✓ macro, split into mechanism + consequence (what TO write):
      current:     the mechanism that's supposed to find your agents only scans the top folder,
                   not subfolders
      consequence: any agent you file in a subfolder is silently invisible — you add one, it
                   never runs, and nothing tells you why

### Item layout — applies to every ✅ and 🤔 item
- **Number every item.** Prefix the title with an emoji digit, sequential within its bucket:
  1️⃣ 2️⃣ 3️⃣ … (past 🔟 use plain `11.`). Title bold, ID after it:
  `1️⃣ **<plain name>** (Code layer: <ID>)`.
- **Bold the label before every colon** — `**修复前**` / `**风险**` / `**现状**` / `**后果**` /
  `**解决方案**`, etc.
- **Align the colons.** Pad with full-width spaces (　) so all colons sit in one vertical column
  report-wide (uniform width = longest label `解决方案`, 4 CJK chars). **The padding goes OUTSIDE
  the bold** — `**风险**　　：`, never `**风险　　**：`. A full-width space right before a closing
  `**` makes the terminal render the `**` literally (bold breaks).
- **A choice never crams options behind `/`.** Break each option onto its own line, labeled
  `【方案 1】` / `【方案 2】` … (English report: `【Option 1】` / `【Option 2】`; NOT emoji digits — those are reserved for the item-level numbering),
  indented under the label — never join them with `/` or `;`:

      **解决方案**：
      　【方案 1】 <option one, in role/effect terms>
      　【方案 2】 <option two>

### Plain, concrete Chinese — no abstract jargon
Reader thinks in visible effects, not metaphors. Ban vague terms (悬空 / 漂移 / 脱节); name the
concrete thing the user would actually see:

    ✗ 体检立刻判这个角色"悬空"
    ✓ 体检报一条红、说"这个角色谁都路由不到" —— 其实它好好挂在子目录里,只是发现机制没扫到,纯误判

Swap: 悬空→查无登记 / 找不到对应记录　·　漂移→对不上 / 不一致　·　脱节→下游引用失效 / 对不上。

### ✅ Safe to fix now
Pure fixes (🟢): something meant to work is broken/unwired; fixing only restores it, logic
unchanged, nothing working regresses.

    1️⃣ **<plain name>** (Code layer: <ID>)
    **修复前**　：<bad effect the user sees in their workflow>
    **修复后**　：<normal effect once fixed>
    **风险**　　：低；only touches the already-broken path

### 🤔 Needs your decision
Judgment calls (🟡/🔴): a design fork, or a change touching a path that currently runs.

    1️⃣ **<plain name>** (Code layer: <ID>)
    **现状**　　：<the mechanism itself — how this part works now, macro level, by role not file>
    **后果**　　：<what that causes the user — the cost; name a silent break here when that's the real risk (an action → break with no error)>
    **解决方案**：
    　【方案 1】 <option one, in role/effect terms>
    　【方案 2】 <option two>
    **建议**　　：<your pick, what it touches, "won't change automatically">

### 现状 vs 后果 — keep them distinct
The split is the whole point; don't let the two collapse into one sentence:
- **现状 (mechanism)** = how the moving part works *right now* — a state, named by role not file.
  No trigger, no blame, just "this is the setup."
- **后果 (consequence)** = what that setup *costs* the user. When the real risk is a silent
  break, name it here: a specific *action the user takes* → a break that fires with **no error**.
  One concrete sentence.

There is no separate silent-break line — the worst silent break lives inside 后果.

## Closing question
One line: offer to apply the ✅ Safe-to-fix items now, leave the 🤔 decision items.

## Mapping
- 🟢 → Safe to fix now　·　🟡 / 🔴 → Needs your decision
- Severity (XHigh/High/Medium/Low) lives in the Code layer; the bucket lives in the decision
  layer. Independent — an XHigh with a 🟢 fix is a "Safe to fix now" item.
