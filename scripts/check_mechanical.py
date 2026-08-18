#!/usr/bin/env python3
"""check_mechanical.py - mechanical grep slice for harness-check Step 2 (dims 3/4).

Measures the target; conviction stays with the model. Four purely
mechanical scans, raw material for failure-patterns dims 3/4:
  1. swallow      - error suppression in script files: `2>/dev/null`,
                    `|| true`, `|| :`, python `except: pass/continue`
                    (dim3 silent-error-swallowing; a hit may be legitimate)
  2. empty        - empty dirs (incl. .gitkeep-only) and empty/placeholder
                    configs (0 bytes or bare {} / [] / null) (dim4)
  3. hardcoded    - user-absolute paths (/Users/<x>, /home/<x>, C:\\Users)
                    in scripts/configs (dim4 portability / residue)
  4. example-only - *.example / *.sample / *.template with no deployed
                    sibling (dim4 missing dependency; a gitignored .env
                    next to .env.example is a legitimate miss - model judges)

Same split as check_discovery.py: measurement left to the model is where
silent skips live; legitimacy needs context and is NOT scripted. Symlinked
dirs are not descended - link topology is check_discovery.py's job. Grep
hits include comments/docstrings (runtime-inert lines) by design - raw
material, the model convicts.

Usage: python3 check_mechanical.py <target_root>
Exit:  0 = measurements printed; 2 = bad invocation or unreadable target.
"""
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
             ".history", ".DS_Store", "dist", "build"}
SCRIPT_SUFFIX = {".sh", ".bash", ".zsh", ".py", ".js", ".mjs", ".cjs",
                 ".ts", ".rb", ".pl"}
SCRIPT_NAMES = {"Makefile", "makefile", "Justfile", "justfile"}
CONFIG_SUFFIX = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}
TEMPLATE_SUFFIX = (".example", ".sample", ".template")
KEEP_ONLY = {".gitkeep", ".keep", ".DS_Store"}
MAX_FILE = 512 * 1024   # larger files skipped (minified bundles) - counted, never silent
PRINT_CAP = 25          # per class; overflow printed as an explicit +N line
WALK_BUDGET = 50000

SWALLOW = re.compile(r"2>\s*/dev/null|\|\|\s*true\b|\|\|\s*:\s*(?:$|;|#)")
HARDCODED = re.compile(r"(?:/Users|/home)/[A-Za-z0-9_][A-Za-z0-9_.\-]*(?:/|\b)"
                       r"|[A-Za-z]:\\\\?Users\\\\?")
_BUDGET = {"n": 0, "hit": False}


def _spend() -> bool:
    _BUDGET["n"] += 1
    if _BUDGET["n"] > WALK_BUDGET:
        if not _BUDGET["hit"]:
            _BUDGET["hit"] = True
            print(f"[check-mechanical] WARNING: traversal TRUNCATED at {WALK_BUDGET} "
                  f"entries - all counts are lower bounds")
        return False
    return True


def is_script(p: Path) -> bool:
    return p.suffix in SCRIPT_SUFFIX or p.name in SCRIPT_NAMES


def is_config(p: Path) -> bool:
    return p.suffix in CONFIG_SUFFIX or p.name == ".env"


def read_lines(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


def py_swallow_hits(lines):
    """`except ...: pass|continue` - inline or on the next non-blank line."""
    hits = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s.startswith("except"):
            continue
        if re.match(r"except\b[^:]*:\s*(pass|continue)\b", s):
            hits.append((i + 1, s))
            continue
        if s.rstrip().endswith(":"):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].split("#")[0].strip() in ("pass", "continue"):
                hits.append((i + 1, s))
    return hits


def emit(tag: str, rows: list):
    for row in rows[:PRINT_CAP]:
        print(f"[check-mechanical]   {row}")
    if len(rows) > PRINT_CAP:
        print(f"[check-mechanical]   (+{len(rows) - PRINT_CAP} more {tag} hits not printed)")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_mechanical.py <target_root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser()
    if not root.is_dir():
        print(f"[check-mechanical] ERROR: {root} is not a directory", file=sys.stderr)
        return 2
    print(f"[check-mechanical] root: {root}")

    files, empty_dirs, unreadable = [], [], []
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = list(d.iterdir())
        except OSError:
            unreadable.append(d)
            continue
        if d != root and all(e.name in KEEP_ONLY for e in entries):
            note = "" if not entries else " (placeholder-only)"
            empty_dirs.append(f"EMPTY-DIR {d.relative_to(root)}/{note}")
        for p in entries:
            if p.name in SKIP_DIRS:
                continue
            if not _spend():
                stack.clear()
                break
            if p.is_dir():
                if not p.is_symlink():
                    stack.append(p)
            elif p.is_file():
                files.append(p)

    swallow, hardcoded, empty_cfg, example_only = [], [], [], []
    sw_files, hc_files = set(), set()
    skipped_large = 0

    for p in files:
        rel = p.relative_to(root)
        for suf in TEMPLATE_SUFFIX:
            if p.name.endswith(suf) and p.name != suf:
                sibling = p.name[: -len(suf)]
                if sibling and not (p.parent / sibling).exists():
                    example_only.append(f"{rel} (no deployed sibling '{sibling}')")
                break
        scr, cfg = is_script(p), is_config(p)
        if not (scr or cfg):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            unreadable.append(p)
            continue
        if size > MAX_FILE:
            skipped_large += 1
            continue
        if cfg and size <= 16:
            try:
                content = p.read_text(encoding="utf-8", errors="replace").strip() if size else ""
            except OSError:
                unreadable.append(p)
                content = None
            if content in ("", "{}", "[]", "null"):
                empty_cfg.append(f"EMPTY-CONFIG {rel} ({size}B)")
        lines = read_lines(p)
        if lines is None:
            unreadable.append(p)
            continue
        for i, ln in enumerate(lines):
            if scr and SWALLOW.search(ln):
                swallow.append(f"{rel}:{i + 1}: {ln.strip()[:90]}")
                sw_files.add(p)
            m = HARDCODED.search(ln)
            if m:
                hardcoded.append(f"{rel}:{i + 1}: {m.group(0)}")
                hc_files.add(p)
        if p.suffix == ".py":
            for lineno, s in py_swallow_hits(lines):
                swallow.append(f"{rel}:{lineno}: {s[:90]} -> pass/continue")
                sw_files.add(p)

    print(f"[check-mechanical] swallow: {len(swallow)} hits in {len(sw_files)} files")
    emit("swallow", swallow)
    print(f"[check-mechanical] empty: dirs={len(empty_dirs)} configs={len(empty_cfg)}")
    emit("empty", empty_dirs + empty_cfg)
    print(f"[check-mechanical] hardcoded: {len(hardcoded)} hits in {len(hc_files)} files")
    emit("hardcoded", hardcoded)
    print(f"[check-mechanical] example-only: {len(example_only)}")
    emit("example-only", example_only)
    if skipped_large:
        print(f"[check-mechanical] skipped-large: {skipped_large} files >{MAX_FILE // 1024}KB not scanned")
    if unreadable:
        dedup = []
        for p in unreadable:
            if p not in dedup:
                dedup.append(p)
        print(f"[check-mechanical] skipped-unreadable: {len(dedup)} - counts are lower bounds")
        emit("unreadable", [f"UNREADABLE {p.relative_to(root)}" for p in dedup])
    print(f"[check-mechanical] summary: swallow={len(swallow)} empty={len(empty_dirs) + len(empty_cfg)} "
          f"hardcoded={len(hardcoded)} example-only={len(example_only)}")
    print("[check-mechanical] NOT scripted (model must convict): whether each hit is "
          "legitimate in its context")
    return 0


if __name__ == "__main__":
    sys.exit(main())
