import "server-only";
import { cache } from "react";
import { and, asc, desc, eq, sql } from "drizzle-orm";
import { db } from "@/db";
import { problems, submissions, testCases } from "@/db/schema";
import type { Problem } from "./problems";
import type { Verdict } from "./judge/runner";
import type { DayActivity } from "./streak";
import type { Difficulty } from "./problems";

export type ProblemSummary = Pick<Problem, "id" | "slug" | "title" | "difficulty" | "tags" | "pattern">;
export type ProblemStatus = "solved" | "attempted";

export interface SubmissionRow {
  id: number;
  verdict: Verdict;
  passed: number;
  total: number;
  runtimeMs: number;
  createdAt: string;
  code: string;
}

export interface SubmissionListRow extends Omit<SubmissionRow, "code"> {
  problemSlug: string;
  problemTitle: string;
}

export async function listProblems(): Promise<ProblemSummary[]> {
  return db
    .select({
      id: problems.id,
      slug: problems.slug,
      title: problems.title,
      difficulty: problems.difficulty,
      tags: problems.tags,
      pattern: problems.patternId,
    })
    .from(problems)
    .orderBy(asc(problems.id));
}

/** The problem with every test case, in the shape the browser judge expects. Cached per request. */
export const getProblem = cache(async (slug: string): Promise<Problem | null> => {
  const [p] = await db.select().from(problems).where(eq(problems.slug, slug)).limit(1);
  if (!p) return null;
  const tests = await db
    .select({ args: testCases.args, expected: testCases.expected, sample: testCases.isSample })
    .from(testCases)
    .where(eq(testCases.problemId, p.id))
    .orderBy(asc(testCases.position));
  return {
    id: p.id,
    slug: p.slug,
    title: p.title,
    difficulty: p.difficulty,
    tags: p.tags,
    description: p.description,
    examples: p.examples,
    constraints: p.constraints,
    functionName: p.functionName,
    params: p.params,
    starterCode: p.starterCode,
    compare: p.compare,
    argTypes: p.argTypes ?? undefined,
    returnType: p.returnType ?? undefined,
    outArg: p.outArg ?? undefined,
    design: p.design || undefined,
    pattern: p.patternId,
    tests,
  };
});

export async function getProblemIdBySlug(slug: string): Promise<number | null> {
  const [p] = await db.select({ id: problems.id }).from(problems).where(eq(problems.slug, slug)).limit(1);
  return p?.id ?? null;
}

/** slug → solved/attempted for every problem the user has submitted to. */
export async function getUserStatuses(userId: string): Promise<Record<string, ProblemStatus>> {
  const rows = await db
    .select({
      slug: problems.slug,
      solved: sql<boolean>`bool_or(${submissions.verdict} = 'Accepted')`,
    })
    .from(submissions)
    .innerJoin(problems, eq(problems.id, submissions.problemId))
    .where(eq(submissions.userId, userId))
    .groupBy(problems.slug);
  return Object.fromEntries(rows.map((r) => [r.slug, r.solved ? "solved" : "attempted"]));
}

const toIso = (d: Date) => d.toISOString();

export async function getProblemSubmissions(userId: string, problemId: number, limit = 50): Promise<SubmissionRow[]> {
  const rows = await db
    .select({
      id: submissions.id,
      verdict: submissions.verdict,
      passed: submissions.passed,
      total: submissions.total,
      runtimeMs: submissions.runtimeMs,
      createdAt: submissions.createdAt,
      code: submissions.code,
    })
    .from(submissions)
    .where(and(eq(submissions.userId, userId), eq(submissions.problemId, problemId)))
    .orderBy(desc(submissions.createdAt))
    .limit(limit);
  return rows.map((r) => ({ ...r, createdAt: toIso(r.createdAt) }));
}

export async function getRecentSubmissions(userId: string, limit = 100): Promise<SubmissionListRow[]> {
  const rows = await db
    .select({
      id: submissions.id,
      verdict: submissions.verdict,
      passed: submissions.passed,
      total: submissions.total,
      runtimeMs: submissions.runtimeMs,
      createdAt: submissions.createdAt,
      problemSlug: problems.slug,
      problemTitle: problems.title,
    })
    .from(submissions)
    .innerJoin(problems, eq(problems.id, submissions.problemId))
    .where(eq(submissions.userId, userId))
    .orderBy(desc(submissions.createdAt))
    .limit(limit);
  return rows.map((r) => ({ ...r, createdAt: toIso(r.createdAt) }));
}

/**
 * Submissions per calendar day (in the user's timezone), all time. One row per active day, so it stays small.
 * Cached per request: the navbar streak and the progress page share it.
 */
export const getActivity = cache(async (userId: string, timeZone: string): Promise<DayActivity[]> => {
  const day = sql<string>`to_char(${submissions.createdAt} at time zone ${timeZone}, 'YYYY-MM-DD')`;
  return db
    .select({
      day,
      submissions: sql<number>`count(*)::int`,
      accepted: sql<number>`(count(*) filter (where ${submissions.verdict} = 'Accepted'))::int`,
    })
    .from(submissions)
    .where(eq(submissions.userId, userId))
    // By position: the timezone is a query parameter, so repeating the expression wouldn't match the SELECT.
    .groupBy(sql`1`)
    .orderBy(sql`1`);
});

export interface DifficultyProgress {
  difficulty: Difficulty;
  solved: number;
  total: number;
}

export async function getSolvedByDifficulty(userId: string): Promise<DifficultyProgress[]> {
  const solvedByUser = sql`exists (
    select 1 from ${submissions}
    where ${submissions.problemId} = ${problems.id}
      and ${submissions.userId} = ${userId}
      and ${submissions.verdict} = 'Accepted'
  )`;
  const rows = await db
    .select({
      difficulty: problems.difficulty,
      total: sql<number>`count(*)::int`,
      solved: sql<number>`(count(*) filter (where ${solvedByUser}))::int`,
    })
    .from(problems)
    .groupBy(problems.difficulty);
  const order: Difficulty[] = ["Easy", "Medium", "Hard"];
  return order.map((d) => rows.find((r) => r.difficulty === d) ?? { difficulty: d, solved: 0, total: 0 });
}

export interface PublicUser {
  id: string;
  name: string;
  image: string | null;
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Public profile fields from Neon Auth's user table (never the email). */
export async function getPublicUser(id: string): Promise<PublicUser | null> {
  if (!UUID.test(id)) return null;
  const { rows } = await db.execute<{ id: string; name: string | null; image: string | null }>(
    sql`select id::text as id, name, image from neon_auth."user" where id = ${id}::uuid and coalesce(banned, false) = false limit 1`,
  );
  const u = rows[0];
  return u ? { id: u.id, name: u.name || "HeapRace user", image: u.image } : null;
}
