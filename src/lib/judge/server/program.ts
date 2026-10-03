import "server-only";
import type { Problem } from "../../problems";
import { HARNESS_PY } from "../harness";

/** Wall-clock limit per test inside the program. Native CPython is much faster than Pyodide. */
export const PER_TEST_LIMIT_SEC = 2;

const MARK = "@@HEAPRACE@@";

/**
 * Runs every test in one process and prints one marked JSON line per test, so user print()
 * output can't be confused with results. A per-test alarm turns an infinite loop into a TLE for
 * that test only (setitimer exists on Linux and macOS, which is where both judges run).
 */
const DRIVER_PY = `
# ---- HeapRace driver ----
import json as _json, signal as _signal, sys as _sys, time as _time

_MARK = "${MARK}"
_fired = False

class _TimeLimit(BaseException):
    pass

def _on_alarm(signum, frame):
    global _fired
    _fired = True
    raise _TimeLimit()

_has_alarm = hasattr(_signal, "setitimer")
if _has_alarm:
    _signal.signal(_signal.SIGALRM, _on_alarm)

# Large tests include deep trees and big grids, so recursive solutions get more room than Python's default 1000.
_sys.setrecursionlimit(10_000)

_real_stdout = _sys.stdout
_payload = _json.loads(_sys.stdin.read())
for _args in _payload["tests"]:
    _fired = False
    _start = _time.perf_counter()
    if _has_alarm:
        _signal.setitimer(_signal.ITIMER_REAL, _payload["timeLimit"])
    try:
        _res = _json.loads(__heaprace_run(
            _payload["code"], _payload["functionName"], _json.dumps(_args),
            _json.dumps(_payload.get("argTypes")), _payload.get("returnType"),
            _json.dumps(_payload.get("options")),
        ))
    except _TimeLimit:
        _res = {}
    finally:
        if _has_alarm:
            _signal.setitimer(_signal.ITIMER_REAL, 0)
    if _fired:
        _res = {"tle": True}
    _res["timeMs"] = (_time.perf_counter() - _start) * 1000
    print(_MARK + _json.dumps(_res), file=_real_stdout, flush=True)
    if _fired:
        break
`;

export const PROGRAM_PY = `${HARNESS_PY}\n${DRIVER_PY}`;

export function buildStdin(problem: Problem, code: string): string {
  return JSON.stringify({
    code,
    functionName: problem.functionName,
    tests: problem.tests.map((t) => t.args),
    argTypes: problem.argTypes ?? null,
    returnType: problem.returnType ?? null,
    options: { outArg: problem.outArg ?? null, design: problem.design ?? false },
    timeLimit: PER_TEST_LIMIT_SEC,
  });
}

export interface TestOutput {
  ok?: boolean;
  tle?: boolean;
  result?: unknown;
  error?: string;
  stdout?: string;
  timeMs: number;
}

export function parseOutput(stdout: string): TestOutput[] {
  return stdout
    .split("\n")
    .filter((line) => line.startsWith(MARK))
    .map((line) => JSON.parse(line.slice(MARK.length)) as TestOutput);
}
