# End-to-End Walkthrough (Step 2.5)

Structural review catches broken PARTS; the walkthrough catches broken CONNECTIONS — every file individually fine, chain dead when run. One simulated run over the real files; no sub-agent is spawned.

## Positive walk (once per audit; skip only when no orchestration exists)

1. Pick ONE typical task — the first thing the harness's own docs promise a user would ask for. Not an edge case; an exhaustive task matrix is a test suite's job, not an audit step.
2. Walk the REAL chain on disk, not the documented one. At each link, verify in files as you go:
   - **trigger** — which always-on rule/keyword routes this task; is the routing decidable mechanically, or does the model have to re-derive it?
   - **dispatch** — which registry/roster entry gets looked up; does the name resolve (cross-check Step 0's inventory)?
   - **execution** — which script/template/role definition actually runs; do its inputs exist where it reads them (config seam)?
   - **reporting** — how does the result get back; does anything check or aggregate it, or can a failure pass silently?
3. Every link that fails to connect = a candidate finding, tagged with the dimension it hits, fed into Step 3 verification like any other.
4. A clean walk is not proof of correctness — only "no break spotted on this path". Name the path walked in the report's blind-spots line.

## Negative walk (ALWAYS, even with no orchestration)

Tests over-trigger — the dilution disease: always-on rules so broad that everything delegates, or a role captures tasks it shouldn't.

1. Craft 1–2 tasks that should NOT trigger delegation or a specific role. Source them from (a) the harness's own trigger words appearing with different intent, (b) two roles whose trigger conditions overlap (dim2 leads from Step 2).
2. Judge each against the always-on config alone — the router never sees a role's body. Would a reasonable model fire? Base the call on the actual rule text, not charitable reading.
3. False-fire → dim2 finding: name the rule doing the over-capture and propose the narrowing (qualify the noun, add a structured "not for …" boundary).
4. No always-on config exists → judge against the roles' own trigger descriptions instead; if there is no trigger surface at all, print `negative: no substrate` in place of the false-fire count and log it in the blind-spots line — a vacuous pass must not look like a tested pass.

## What not to do

- Don't spawn a real sub-agent to run the task — this is a paper walk over real files.
- Don't walk more than one positive task per audit.
- Don't use the walk to score dimensions; it only produces candidate findings.
