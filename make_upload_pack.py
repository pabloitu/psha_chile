# make_upload_pack.py
# Build upload-ready copies of the codebase for the claude.ai project
# knowledge base (flat, so the module namespace must live in filenames).
# Originals untouched — renaming in place would break every import.
#   upload_pack/<module>__<name>.py   first line stamped '# module/name.py'
#   upload_pack/INDEX.md              per module: files, purpose line, mtime
# Run from the repository root. Review INDEX.md (mtimes expose stale
# fault_model files), prune, then upload the pack contents + the pack's
# INDEX.md to the project.

import datetime
import re
import shutil
from pathlib import Path

MODULES = ["sub_interface", "ssm_intraslab", "fault_model",
           "cat_no_mech_handler"]
EXTS = {".py", ".md"}
SKIP_DIRS = {"__pycache__", ".git", ".idea", "figures"}
SKIP_PREFIX = ("outputs",)   # outputs, outputs_z60, ...
OUT = Path("upload_pack")


def purpose(path):
    txt = path.read_text(errors="ignore")
    for line in txt.splitlines()[:6]:
        s = line.strip().lstrip("#").strip()
        if s and not s.startswith(("import", "from", "\"\"\"", "'''")) \
                and path.name not in s:
            return s[:90]
    return ""


def stamp(txt, module, name):
    header = f"# {module}/{name}"
    lines = txt.splitlines()
    if lines and re.match(rf"#\s*{re.escape(name)}\s*$", lines[0].strip()):
        lines[0] = header
    else:
        lines.insert(0, header)
    return "\n".join(lines) + "\n"


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    index, seen = {}, {}
    for module in MODULES:
        root = Path(module)
        if not root.is_dir():
            print(f"[skip] {module}: not found")
            continue
        rows = []
        for p in sorted(root.rglob("*")):
            if p.suffix not in EXTS or not p.is_file():
                continue
            if any(d in p.parts for d in SKIP_DIRS):
                continue
            if any(part.startswith(SKIP_PREFIX) for part in p.parts[1:-1]):
                continue
            new = f"{module}__{p.name}"
            if p.suffix == ".py":
                (OUT / new).write_text(stamp(p.read_text(errors="ignore"),
                                             module, p.name))
            else:
                shutil.copy(p, OUT / new)
            mt = datetime.date.fromtimestamp(p.stat().st_mtime)
            rows.append((p.name, new, str(mt), purpose(p)))
            seen.setdefault(p.name, []).append(module)
        index[module] = rows
        print(f"[{module}] {len(rows)} files")

    lines = ["# INDEX — Chile PSHA codebase (upload pack)",
             "Flat project knowledge; filenames carry the module as "
             "`module__file`. Newest-first mtime exposes stale files.", ""]
    for module, rows in index.items():
        lines += [f"## {module}", "",
                  "| file | uploaded as | modified | purpose |",
                  "|---|---|---|---|"]
        for name, new, mt, why in sorted(rows, key=lambda r: r[2],
                                         reverse=True):
            lines.append(f"| {name} | {new} | {mt} | {why} |")
        lines.append("")

    dups = {n: ms for n, ms in seen.items() if len(ms) > 1}
    if dups:
        lines += ["## Name collisions across modules (prefix disambiguates)",
                  ""]
        for n, ms in sorted(dups.items()):
            lines.append(f"- {n}: {', '.join(ms)}")
        lines.append("")
    (OUT / "INDEX.md").write_text("\n".join(lines))
    print(f"\nwrote {sum(len(r) for r in index.values())} files + INDEX.md "
          f"to {OUT}/")
    if dups:
        print("collisions (handled by prefixes): "
              + ", ".join(sorted(dups)))


if __name__ == "__main__":
    main()