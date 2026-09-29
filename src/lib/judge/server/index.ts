import "server-only";
import type { Problem } from "../../problems";
import { isCorrect } from "../compare";
import type { CaseResult, JudgeResult } from "../runner";
import { getBackend, JudgeUnavailableError } from "./backends";
import { buildStdin, parseOutput, PER_TEST_LIMIT_SEC, PROGRAM_PY } from "./program";

export { JudgeUnavailableError };

const MEMORY_KB = 256_000;
/** Judge0 CE caps a submission at 15 s of CPU time by default. */
const MAX_TOTAL_SEC = 15;

/**
 * Judges `code` against every test of `problem` (hidden ones included) on the server.
 * Like most judges it reports the first failing test; passed counts tests before that failure.
 */
export async function judgeOnServer(problem: Problem, code: string): Promise<JudgeResult> {
  const total = problem.tests.length;
  const exec = await getBackend().execute({
    source: PROGRAM_PY,
    stdin: buildStdin(problem, code),
    wallTimeSec: Math.min(MAX_TOTAL_SEC, 1 + total * PER_TEST_LIMIT_SEC),
    memoryKb: MEMORY_KB,
  });

  let outputs;
  try {
    outputs = parseOutput(exec.stdout);
  } catch {
    throw new JudgeUnavailableError("The judge returned output it couldn't read.");
  }

  const cases: CaseResult[] = [];
  for (let index = 0; index < total; index++) {
    const test = problem.tests[index];
    const out = outputs[index];
    let c: CaseResult;
    if (!out) {
      // The process stopped before reporting this test: killed for time or memory, or crashed.
      c =
        exec.status === "time-limit"
          ? { index, test, verdict: "Time Limit Exceeded", stdout: "", timeMs: PER_TEST_LIMIT_SEC * 1000 }
          : {
              index,
              test,
              verdict: "Runtime Error",
              error: [exec.message ?? "Your program stopped unexpectedly.", exec.stderr.trim().split("\n").slice(-5).join("\n")]
                .filter(Boolean)
                .join("\n"),
              stdout: "",
              timeMs: 0,
            };
    } else if (out.tle) {
      c = { index, test, verdict: "Time Limit Exceeded", stdout: out.stdout ?? "", timeMs: out.timeMs };
    } else if (!out.ok) {
      c = { index, test, verdict: "Runtime Error", error: out.error, stdout: out.stdout ?? "", timeMs: out.timeMs };
    } else {
      const ok = isCorrect(out.result, test.expected, problem.compare);
      c = {
        index,
        test,
        verdict: ok ? "Accepted" : "Wrong Answer",
        actual: out.result,
        stdout: out.stdout ?? "",
        timeMs: out.timeMs,
      };
    }
    cases.push(c);
    if (c.verdict !== "Accepted") break;
  }

  const failed = cases.find((c) => c.verdict !== "Accepted");
  return {
    mode: "submit",
    verdict: failed?.verdict ?? "Accepted",
    // Only the failing case is sent back, so hidden tests that passed stay private.
    cases: failed ? [failed] : [],
    passed: failed ? failed.index : total,
    total,
    timeMs: cases.reduce((sum, c) => sum + c.timeMs, 0),
  };
}
