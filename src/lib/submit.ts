import "server-only";
import { and, eq, gt, sql } from "drizzle-orm";
import { db } from "@/db";
import { submissions } from "@/db/schema";
import type { JudgeResult } from "./judge/runner";
import { judgeOnServer, JudgeUnavailableError } from "./judge/server";
import type { Problem } from "./problems";
import type { SubmissionRow } from "./queries";

export const MAX_CODE_LENGTH = 100_000;
const MAX_SUBMISSIONS_PER_MINUTE = 10;

export type SubmitResult =
  | { ok: true; result: JudgeResult; submission: SubmissionRow }
  | {
      ok: false;
      reason: "signed-out" | "invalid" | "rate-limited" | "judge-unavailable" | "race-closed";
      message: string;
    };

/**
 * Rate-limits, judges on the server against every test, and stores the submission.
 * Callers check authentication and (for races) that the race is open.
 */
export async function judgeAndRecord(opts: {
  userId: string;
  problem: Problem;
  code: string;
  raceRoomId?: number;
}): Promise<SubmitResult> {
  const { userId, problem, code, raceRoomId } = opts;
  if (typeof code !== "string" || code.length > MAX_CODE_LENGTH) {
    return { ok: false, reason: "invalid", message: "That submission isn't valid." };
  }

  const [{ recent }] = await db
    .select({ recent: sql<number>`count(*)::int` })
    .from(submissions)
    .where(and(eq(submissions.userId, userId), gt(submissions.createdAt, sql`now() - interval '1 minute'`)));
  if (recent >= MAX_SUBMISSIONS_PER_MINUTE) {
    return { ok: false, reason: "rate-limited", message: "Too many submissions. Wait a minute and try again." };
  }

  let result: JudgeResult;
  try {
    result = await judgeOnServer(problem, code);
  } catch (e) {
    if (e instanceof JudgeUnavailableError) {
      console.error("[judge]", e.message);
      return { ok: false, reason: "judge-unavailable", message: "The judge is unavailable right now. Try again soon." };
    }
    throw e;
  }

  const failed = result.cases[0];
  const [row] = await db
    .insert(submissions)
    .values({
      userId,
      problemId: problem.id,
      code,
      verdict: result.verdict,
      passed: result.passed,
      total: result.total,
      runtimeMs: Math.round(result.timeMs),
      failedTest: failed ? failed.index : null,
      raceRoomId: raceRoomId ?? null,
    })
    .returning();

  return {
    ok: true,
    result,
    submission: {
      id: row.id,
      verdict: row.verdict,
      passed: row.passed,
      total: row.total,
      runtimeMs: row.runtimeMs,
      createdAt: row.createdAt.toISOString(),
      code: row.code,
    },
  };
}
