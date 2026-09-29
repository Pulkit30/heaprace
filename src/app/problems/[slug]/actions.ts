"use server";

import { db } from "@/db";
import { submissions } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth/server";
import { getProblemIdBySlug, type SubmissionRow } from "@/lib/queries";
import type { Verdict } from "@/lib/judge/runner";

const VERDICTS: Verdict[] = ["Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded"];
const MAX_CODE_LENGTH = 100_000;

export interface SubmissionInput {
  slug: string;
  code: string;
  verdict: Verdict;
  passed: number;
  total: number;
  runtimeMs: number;
  failedTest: number | null;
}

export type SaveSubmissionResult =
  | { ok: true; submission: SubmissionRow }
  | { ok: false; reason: "signed-out" | "invalid" };

const isCount = (n: unknown): n is number => Number.isInteger(n) && (n as number) >= 0 && (n as number) <= 10_000;

/**
 * Stores a browser-judged submission. Phase 2 trusts the verdict the browser sends;
 * Phase 3 replaces this with judging on the server.
 */
export async function saveSubmission(input: SubmissionInput): Promise<SaveSubmissionResult> {
  const user = await getCurrentUser();
  if (!user) return { ok: false, reason: "signed-out" };

  const valid =
    typeof input?.slug === "string" &&
    typeof input.code === "string" &&
    input.code.length <= MAX_CODE_LENGTH &&
    VERDICTS.includes(input.verdict) &&
    isCount(input.passed) &&
    isCount(input.total) &&
    input.passed <= input.total &&
    (input.verdict === "Accepted") === (input.passed === input.total) &&
    Number.isFinite(input.runtimeMs) &&
    input.runtimeMs >= 0 &&
    (input.failedTest === null || isCount(input.failedTest));
  if (!valid) return { ok: false, reason: "invalid" };

  const problemId = await getProblemIdBySlug(input.slug);
  if (problemId === null) return { ok: false, reason: "invalid" };

  const [row] = await db
    .insert(submissions)
    .values({
      userId: user.id,
      problemId,
      code: input.code,
      verdict: input.verdict,
      passed: input.passed,
      total: input.total,
      runtimeMs: Math.round(input.runtimeMs),
      failedTest: input.failedTest,
    })
    .returning();

  return {
    ok: true,
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
