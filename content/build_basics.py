"""Builds the extra hidden tests for the 31 hand-written problems in src/lib/problems.ts.

Reads [{slug, functionName, argTypes, returnType, compare, tests}] (the hand-written problems) as JSON on stdin,
takes extra inputs from content/basics_extra.py (edge cases, generated inputs and large timing tests), computes
expected outputs with the reference solutions in scripts/reference_solutions.py, cross-checks against a brute force
where one is given, and prints {slug: [tests]} as JSON. The rules match content/build_catalog.py.

Usage: python3 content/build_basics.py < problems.json > extra.json
"""

import copy
import importlib.util
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.setrecursionlimit(100_000)

import build_catalog as cat  # noqa: E402
import catalog_lib as lib  # noqa: E402

spec = importlib.util.spec_from_file_location("reference_solutions", HERE.parent / "scripts" / "reference_solutions.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)

from basics_extra import EXTRA  # noqa: E402


def run(p, impl, args):
    args = copy.deepcopy(args)
    arg_types = p.get("argTypes") or []
    built = [ref.BUILD[arg_types[i]](a) if i < len(arg_types) and arg_types[i] else a for i, a in enumerate(args)]
    result = impl(*built)
    if p.get("returnType"):
        result = ref.DUMP[p["returnType"]](result)
    return cat.normalize(result)


def build():
    problems = json.load(sys.stdin)
    by_slug = {p["slug"]: p for p in problems}
    unknown = sorted(set(EXTRA) - set(by_slug))
    if unknown:
        raise SystemExit(f"basics_extra: unknown slugs {unknown}")
    errors, out = [], {}
    for p in problems:
        slug = p["slug"]
        more = EXTRA.get(slug, {})
        try:
            impl = getattr(ref.REFERENCE[slug](), p["functionName"])
            keys = {json.dumps(cat.normalize(t["args"])) for t in p["tests"]}
            hidden = sum(1 for t in p["tests"] if not t.get("sample"))
            tests = []
            raw = [(a, True) for a in more.get("edge", [])] + [(a, False) for a in more.get("edge_nb", [])]
            gen = more.get("gen")
            for i in range(more.get("n", 0) if gen else 0):
                raw.append((gen(lib.Gen(f"basics:{slug}:{i}")), True))
            for args, check in raw:
                args = cat.normalize(list(args))
                key = json.dumps(args)
                if key in keys:
                    continue
                keys.add(key)
                if len(key) > cat.MAX_TEST_CHARS:
                    raise ValueError(f"test input too large ({len(key)} chars)")
                expected = run(p, impl, args)
                if check and more.get("brute"):
                    other = run(p, more["brute"], args)
                    if not cat.same(expected, other, p["compare"]):
                        raise ValueError(f"reference and brute force disagree on {key[:200]}: {expected!r} vs {other!r}")
                tests.append({"args": args, "expected": expected})
            for i, make in enumerate(more.get("large", [])):
                args = cat.normalize(list(make(lib.Gen(f"basics:{slug}:large:{i}"))))
                key = json.dumps(args)
                if key in keys:
                    continue
                keys.add(key)
                if len(key) > cat.MAX_LARGE_CHARS:
                    raise ValueError(f"large test {i} too big ({len(key)} chars)")
                expected, took = cat.timed(lambda: run(p, impl, args))
                if took > cat.LARGE_REF_SEC:
                    raise ValueError(f"large test {i}: reference took {took:.2f}s (limit {cat.LARGE_REF_SEC}s)")
                tests.append({"args": args, "expected": expected})
            if hidden + len(tests) < cat.MIN_HIDDEN:
                raise ValueError(f"only {hidden + len(tests)} hidden tests (need {cat.MIN_HIDDEN})")
            out[slug] = tests
        except Exception as e:  # noqa: BLE001
            errors.append(f"{slug}: {e}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    build()
