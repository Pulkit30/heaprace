"""Builds the HeapRace problem catalog.

Imports every module in content/catalog/, runs each reference solution on its sample, explicit and generated
tests to compute expected outputs, cross-checks against a brute-force solution when one is provided, validates
the tutor guide, and prints the result as JSON (consumed by scripts/seed.ts and scripts/verify-problems.ts).
Problem ids are kept stable in content/ids.json so saved submissions never point at the wrong problem.

Each catalog module may also define EXTRA = {slug: {"edge": [args, ...], "large": [gen, ...]}}:
  - edge: hand-picked edge-case inputs (checked against the brute force like any other test);
  - edge_nb: edge cases too big for the brute force (boundary values), computed by the reference only;
  - large: generators for near-limit inputs that a correct but slow (e.g. O(n²)) solution fails on time.
    They skip the brute force, may be up to MAX_LARGE_CHARS, and the reference must finish within
    LARGE_REF_SEC locally so an efficient solution passes comfortably on Judge0.

Usage: python3 content/build_catalog.py [--existing-slugs a,b,c] [--report] > catalog.json
"""

import copy
import importlib.util
import json
import pathlib
import sys
import time
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.setrecursionlimit(100_000)

import catalog_lib as lib  # noqa: E402

IDS_FILE = HERE / "ids.json"
FIRST_CATALOG_ID = 32  # the hand-written problems in src/lib/problems.ts use 1–31
MAX_TEST_CHARS = 30_000
MAX_LARGE_CHARS = 150_000
LARGE_REF_SEC = 0.35
MIN_HIDDEN = 6
MAX_EXPECTED_CHARS = 60_000
DIFFICULTIES = {"Easy", "Medium", "Hard"}
COMPARES = {"exact", "unordered", "unordered-deep", "approx"}


def normalize(v):
    return json.loads(json.dumps(v))


def same(a, b, mode):
    if mode == "approx":
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
            return abs(a - b) <= 1e-5 * max(1, abs(b))
        if isinstance(a, list) and isinstance(b, list):
            return len(a) == len(b) and all(same(x, y, mode) for x, y in zip(a, b))
        return a == b
    if mode in ("unordered", "unordered-deep") and isinstance(a, list) and isinstance(b, list):
        key = lambda x: json.dumps(x, sort_keys=True)  # noqa: E731
        if mode == "unordered-deep":
            a = [sorted(x, key=key) if isinstance(x, list) else x for x in a]
            b = [sorted(x, key=key) if isinstance(x, list) else x for x in b]
        return sorted(a, key=key) == sorted(b, key=key)
    return a == b


def timed(fn, tries=3):
    """Result and the best of up to `tries` timings, so a busy machine doesn't fail the build."""
    best = None
    for _ in range(tries):
        start = time.perf_counter()
        result = fn()
        took = time.perf_counter() - start
        best = took if best is None else min(best, took)
        if best <= LARGE_REF_SEC:
            break
    return result, best


def run(meta, impl, args):
    """Run a reference/brute implementation exactly the way the judge runs user code."""
    args = copy.deepcopy(args)
    if meta.get("design"):
        ops, op_args = args
        obj, out = None, []
        for op, a in zip(ops, op_args):
            if op == meta["cls"]:
                obj = impl(*a)
                out.append(None)
            else:
                out.append(getattr(obj, op)(*a))
        return normalize(out)
    arg_types = meta.get("arg_types") or []
    built = [lib.BUILD[arg_types[i]](a) if i < len(arg_types) and arg_types[i] else a for i, a in enumerate(args)]
    result = impl(*built)
    out_arg = meta.get("out_arg")
    if out_arg is not None:
        result = built[out_arg]
        if out_arg < len(arg_types) and arg_types[out_arg] in lib.DUMP:
            result = lib.DUMP[arg_types[out_arg]](result)
    elif meta.get("ret"):
        result = lib.DUMP[meta["ret"]](result)
    return normalize(result)


def starter_code(meta):
    if meta.get("starter"):
        return meta["starter"].strip("\n") + "\n"
    lines = []
    types = set(meta.get("arg_types") or []) | ({meta["ret"]} if meta.get("ret") else set())
    if types & {"ListNode", "CycleList", "NodeIndex", "ListNodeArray"}:
        lines += [
            "# ListNode is provided by the judge:",
            "# class ListNode:",
            "#     def __init__(self, val=0, next=None):",
            "#         self.val = val",
            "#         self.next = next",
            "",
        ]
    if types & {"TreeNode", "TreeNodeArray"}:
        lines += [
            "# TreeNode is provided by the judge:",
            "# class TreeNode:",
            "#     def __init__(self, val=0, left=None, right=None):",
            "#         self.val = val",
            "#         self.left = left",
            "#         self.right = right",
            "",
        ]
    if meta.get("imports"):
        lines += [meta["imports"], ""]
    lines += ["class Solution:", f"    def {meta['sig']}:", "        pass", ""]
    return "\n".join(lines)


def build():
    existing = set()
    if "--existing-slugs" in sys.argv:
        existing = set(sys.argv[sys.argv.index("--existing-slugs") + 1].split(","))

    extra = {}
    for path in sorted((HERE / "catalog").glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"catalog_{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for slug, more in getattr(module, "EXTRA", {}).items():
            if slug in extra:
                raise SystemExit(f"{slug}: EXTRA defined twice")
            extra[slug] = more
    known = {m["slug"] for m in lib.REGISTRY}
    unknown = sorted(set(extra) - known)
    if unknown:
        raise SystemExit(f"EXTRA for unknown slugs: {unknown}")
    report = []

    ids = json.loads(IDS_FILE.read_text()) if IDS_FILE.exists() else {}
    next_id = max([FIRST_CATALOG_ID - 1, *ids.values()]) + 1
    errors, out, seen = [], [], set()

    for meta in lib.REGISTRY:
        slug = meta["slug"]
        where = f"{slug}"
        started = time.perf_counter()
        try:
            if slug in seen or slug in existing:
                raise ValueError("duplicate slug")
            seen.add(slug)
            if meta["difficulty"] not in DIFFICULTIES:
                raise ValueError("bad difficulty")
            compare = meta.get("compare", "exact")
            if compare not in COMPARES:
                raise ValueError("bad compare mode")
            hints = meta["hints"]
            if len(hints) != 3 or any(len(h) < 20 for h in hints):
                raise ValueError("need 3 real hints")
            guide_text = [*hints, meta["insight"], *meta["pitfalls"]]
            if any(lib.looks_like_code(t) for t in guide_text):
                raise ValueError("guide text looks like code")
            if not meta["pitfalls"]:
                raise ValueError("need at least one pitfall")

            if meta.get("design"):
                fn, params = meta["cls"], ["operations", "arguments"]
            else:
                fn, params = lib.parse_signature(meta["sig"])

            impl = meta["solve"]
            samples = meta["samples"]
            if len(samples) < 2:
                raise ValueError("need at least 2 samples")
            more = extra.get(slug, {})
            raw = [(tuple(a), True) for a in samples] + [(tuple(a), False) for a in meta.get("tests", [])]
            raw += [(tuple(a), False) for a in more.get("edge", [])]
            no_brute = {json.dumps(normalize(list(a))) for a in more.get("edge_nb", [])}
            raw += [(tuple(a), False) for a in more.get("edge_nb", [])]
            gen = meta.get("gen")
            if gen:
                for i in range(meta.get("n", 6)):
                    raw.append((tuple(gen(lib.Gen(f"{slug}:{i}"))), False))

            tests, keys = [], set()
            for args, sample in raw:
                args = normalize(list(args))
                key = json.dumps(args)
                if key in keys:
                    continue
                keys.add(key)
                if len(key) > MAX_TEST_CHARS:
                    raise ValueError(f"test input too large ({len(key)} chars)")
                expected = run(meta, impl, args)
                if meta.get("brute") and key not in no_brute:
                    other = run(meta, meta["brute"], args)
                    if not same(expected, other, compare):
                        raise ValueError(f"reference and brute force disagree on {key[:200]}: {expected!r} vs {other!r}")
                if len(json.dumps(expected)) > MAX_EXPECTED_CHARS:
                    raise ValueError(f"expected output too large for {key[:80]}")
                tests.append({"args": args, "expected": expected, **({"sample": True} if sample else {})})
            if len(tests) < 5:
                raise ValueError(f"only {len(tests)} distinct tests")

            large = 0
            for i, make in enumerate(more.get("large", [])):
                args = normalize(list(make(lib.Gen(f"{slug}:large:{i}"))))
                key = json.dumps(args)
                if key in keys:
                    continue
                keys.add(key)
                if len(key) > MAX_LARGE_CHARS:
                    raise ValueError(f"large test {i} too big ({len(key)} chars)")
                expected, took = timed(lambda: run(meta, impl, args))
                if took > LARGE_REF_SEC:
                    raise ValueError(f"large test {i}: reference took {took:.2f}s (limit {LARGE_REF_SEC}s)")
                if len(json.dumps(expected)) > MAX_LARGE_CHARS:
                    raise ValueError(f"large test {i}: expected output too large")
                tests.append({"args": args, "expected": expected})
                large += 1
            hidden = sum(1 for t in tests if not t.get("sample"))
            if hidden < MIN_HIDDEN:
                raise ValueError(f"only {hidden} hidden tests (need {MIN_HIDDEN})")
            report.append(f"{slug}\t{hidden}\t{large}\t{len(more.get('edge', []))}\t{time.perf_counter() - started:.2f}s")

            examples = []
            notes = meta.get("notes", {})
            for i, t in enumerate(tests[:2]):
                examples.append({
                    "input": ", ".join(f"{p} = {lib.fmt(v)}" for p, v in zip(params, t["args"])),
                    "output": lib.fmt(t["expected"]),
                    **({"explanation": notes[i]} if i in notes else {}),
                })

            if slug not in ids:
                ids[slug] = next_id
                next_id += 1

            out.append({
                "id": ids[slug],
                "slug": slug,
                "title": meta["title"],
                "difficulty": meta["difficulty"],
                "pattern": meta["pattern"],
                "tags": meta["tags"],
                "description": meta["desc"].strip(),
                "examples": examples,
                "constraints": meta["constraints"],
                "functionName": fn,
                "params": params,
                "starterCode": starter_code(meta),
                "compare": compare,
                **({"argTypes": meta["arg_types"]} if meta.get("arg_types") else {}),
                **({"returnType": meta["ret"]} if meta.get("ret") else {}),
                **({"outArg": meta["out_arg"]} if meta.get("out_arg") is not None else {}),
                **({"design": True} if meta.get("design") else {}),
                "tests": tests,
                "guide": {
                    "hints": hints,
                    "insight": meta["insight"],
                    "complexity": {"time": meta["time"], "space": meta["space"], **({"note": meta["note"]} if meta.get("note") else {})},
                    "pitfalls": meta["pitfalls"],
                },
            })
        except Exception as e:  # noqa: BLE001
            errors.append(f"{where}: {e}\n" + "".join(traceback.format_exception(e)[-3:-1]) if not isinstance(e, ValueError) else f"{where}: {e}")

    IDS_FILE.write_text(json.dumps(ids, indent=0, sort_keys=True) + "\n")
    if "--report" in sys.argv:
        print("slug\thidden\tlarge\tedge\tbuild\n" + "\n".join(report), file=sys.stderr)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    build()
