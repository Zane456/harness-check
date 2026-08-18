#!/usr/bin/env python3
"""check_discovery.py - mechanical measurements for harness-check Step 0.

Measures the target harness; judgment stays with the model. Covers the
purely mechanical slice of the discovery lifeline:
  1. dead symlinks (find -type l with a broken target)
  2. glob coverage: for each role/agent/skill-like dir, top-level *.md
     count vs recursive count - a gap means a single-level glob misses files
  3. name inventory: filename stem vs frontmatter `name:` per md file,
     raw material for the registry / naming / forced-trigger comparisons
     the model must still do by reading the registry and dispatcher.

Two traversals, both SKIP_DIRS-pruned, sharing one entry budget that
aborts with an explicit TRUNCATED line (never a silent cap):
- discovery pass over the whole root: yields everything once; descends
  a dir symlink only when its target is OUTSIDE the root and not an
  ancestor of it (the symlink-installed-package case) - in-root targets
  are covered physically, ancestor targets would swallow parent trees.
- attribution pass per candidate dir: follows its LOGICAL tree
  (including in-root symlinks, e.g. skills/pkg -> ../vendored/pkg) so
  every md is attributed to the dir a discovery glob would reach it
  from; only root-ancestor targets are refused. Candidate aliases are
  deduped by resolved identity (physical dir wins over a symlink), and
  the inventory is deduped by resolved file identity.

Rationale: these three only need measurement, and measurement left to
the model is where silent skips live. Registry completeness and
forced-trigger resolvability need project understanding - NOT scripted.

Usage: python3 check_discovery.py <target_root>
Exit:  0 = measurements printed; 2 = bad invocation or unreadable target.
"""
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
             ".history", ".DS_Store", "dist", "build"}
CANDIDATE_DIR = re.compile(r"(?i)^(agents?|roles?|skills?|commands?|members?|teams?|workers?)$")
WALK_BUDGET = 50000
_BUDGET = {"n": 0, "hit": False}
_UNREADABLE = []


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def _spend() -> bool:
    _BUDGET["n"] += 1
    if _BUDGET["n"] > WALK_BUDGET:
        if not _BUDGET["hit"]:
            _BUDGET["hit"] = True
            print(f"[check-discovery] WARNING: traversal TRUNCATED at {WALK_BUDGET} "
                  f"entries (runaway symlink target?) - all counts are lower bounds")
        return False
    return True


def _resolve(p: Path):
    try:
        return p.resolve()
    except OSError:
        return None


def walk(root: Path, rroot: Path):
    """Discovery pass - see module docstring."""
    seen, stack = set(), [root]
    while stack:
        d = stack.pop()
        rp = _resolve(d)
        if rp is None or rp in seen:
            continue
        seen.add(rp)
        try:
            entries = list(d.iterdir())
        except OSError:
            _UNREADABLE.append(d)
            continue
        for p in entries:
            if p.name in SKIP_DIRS:
                continue
            if not _spend():
                return
            yield p
            if not p.is_dir():
                continue
            if p.is_symlink():
                tgt = _resolve(p)
                if tgt is None or tgt.is_relative_to(rroot) or rroot.is_relative_to(tgt):
                    continue
            stack.append(p)


def crawl_md(d: Path, rroot: Path):
    """Attribution pass - all md in d's LOGICAL tree; see module docstring."""
    out, seen, stack = [], set(), [d]
    while stack:
        cur = stack.pop()
        rp = _resolve(cur)
        if rp is None or rp in seen:
            continue
        seen.add(rp)
        try:
            entries = list(cur.iterdir())
        except OSError:
            _UNREADABLE.append(cur)
            continue
        for p in entries:
            if p.name in SKIP_DIRS:
                continue
            if not _spend():
                return out
            if p.is_dir():
                if p.is_symlink():
                    tgt = _resolve(p)
                    if tgt is None or rroot.is_relative_to(tgt):
                        continue
                stack.append(p)
            elif p.suffix == ".md" and p.is_file():  # skip broken md symlinks
                out.append(p)
    return out


def frontmatter_name(md: Path):
    try:
        head = md.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")[:8192]
    except OSError:
        return None
    m = re.match(r"(?s)^---\n(.*?)\n---", head)
    if not m:
        # opening fence but no closing one inside the 8KB window - flag, don't silently skip
        return "\x00unterminated" if head.startswith("---\n") else None
    nm = re.search(r"(?m)^name:\s*(.+)$", m.group(1))
    return nm.group(1).strip().strip("'\"") if nm else None


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_discovery.py <target_root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser()
    if not root.is_dir():
        print(f"[check-discovery] ERROR: {root} is not a directory", file=sys.stderr)
        return 2
    rroot = _resolve(root) or root

    print(f"[check-discovery] root: {root}")
    paths = list(walk(root, rroot))
    nfiles = sum(1 for p in paths if p.is_file())
    print(f"[check-discovery] files-walked: {nfiles} files ({len(paths)} entries)")

    dead = [p for p in paths if p.is_symlink() and not p.exists()]
    print(f"[check-discovery] dead-symlinks: {len(dead)}")
    for p in dead:
        print(f"[check-discovery]   BROKEN {p.relative_to(root)} -> {p.readlink()}")

    cand_dirs = [p for p in paths if p.is_dir() and CANDIDATE_DIR.match(p.name)]
    # de-nest lexically (teams/roles/), then de-alias by resolved identity
    # with the physical dir winning over a symlink alias
    cand_dirs = [d for d in cand_dirs
                 if not any(o != d and o in d.parents for o in cand_dirs)]
    by_target = {}
    for d in sorted(cand_dirs, key=lambda p: (p.is_symlink(), str(p))):
        by_target.setdefault(_resolve(d) or d, d)
    cand_dirs = sorted(by_target.values())

    md_of = {d: crawl_md(d, rroot) for d in cand_dirs}

    if not cand_dirs:
        print("[check-discovery] glob-coverage: no agent/role/skill-like dirs found "
              "(non-standard layout - model must locate the discovery dirs itself)")
    for d in cand_dirs:
        try:
            listing = list(d.iterdir())
        except OSError:
            _UNREADABLE.append(d)
            print(f"[check-discovery] glob-coverage: {_rel(d, root)}/ UNREADABLE - skipped")
            continue
        top = sum(1 for f in listing
                  if f.is_file() and f.suffix == ".md" and f.name not in SKIP_DIRS)
        rec = len(md_of[d])
        gap = rec - top
        subdirs = [s for s in listing if s.is_dir() and s.name not in SKIP_DIRS]
        skill_pkgs = sum(1 for s in subdirs if (s / "SKILL.md").is_file())
        # measurement only - whether the harness's ACTUAL glob is single-level
        # is the model's to verify; these lines are leads, not verdicts
        if _BUDGET["hit"]:
            verdict = "unknown (walk truncated - counts are lower bounds)"
        elif gap > 0 and subdirs and skill_pkgs > len(subdirs) / 2:
            verdict = (f"skill-package layout ({skill_pkgs}/{len(subdirs)} subdirs have "
                       f"SKILL.md) - a *.md glob misses these, */SKILL.md reaches them "
                       f"(verify the actual glob)")
        elif gap > 0:
            verdict = f"a single-level glob would miss {gap} (verify the actual glob)"
        else:
            verdict = "flat - no gap for a single-level glob"
        print(f"[check-discovery] glob-coverage: {_rel(d, root)}/ "
              f"top-level={top} recursive={rec} - {verdict}")

    mismatches = 0
    inventory = 0
    seen_files = set()
    # physical paths first ACROSS all dirs so an alias never claims (or mis-stems) the real file
    all_md = [md for d in cand_dirs for md in md_of[d]]
    for md in sorted(all_md, key=lambda p: (p.is_symlink(), str(p))):
        if md.name.upper() == "README.MD":
            continue
        rp = _resolve(md) or md
        if rp in seen_files:
            continue
        seen_files.add(rp)
        inventory += 1
        declared = frontmatter_name(md)
        stem = md.stem if md.name != "SKILL.md" else md.parent.name
        if declared == "\x00unterminated":
            print(f"[check-discovery]   NOTE {_rel(md, root)}: frontmatter opens but no "
                  f"closing '---' within 8KB - name unchecked")
        elif declared and declared != stem:
            mismatches += 1
            print(f"[check-discovery]   NAME-MISMATCH {_rel(md, root)}: "
                  f"frontmatter '{declared}' vs path-derived '{stem}'")
    print(f"[check-discovery] name-inventory: {inventory} md files in {len(cand_dirs)} "
          f"candidate dirs, {mismatches} frontmatter/path mismatches")
    if _UNREADABLE:
        uniq = list(dict.fromkeys(_rel(p, root) for p in _UNREADABLE))
        shown = ", ".join(uniq[:5])
        more = ", …" if len(uniq) > 5 else ""
        print(f"[check-discovery] skipped-unreadable: {len(uniq)} dir(s) "
              f"({shown}{more}) - counts are lower bounds")
    print("[check-discovery] NOT scripted (model must verify by reading): registry "
          "completeness, dispatcher naming, forced-trigger targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
