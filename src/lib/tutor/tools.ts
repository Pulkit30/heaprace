import "server-only";
import { and, asc, eq, isNull, ne, or, sql } from "drizzle-orm";
import { db } from "@/db";
import { kbChunks, problems } from "@/db/schema";
import { patterns } from "../roadmap";
import { errorGuides } from "./knowledge";

// The tutor's tools. The in-app agent (engine.ts) and the MCP server (/api/mcp) both call these,
// so an external AI assistant sees exactly the same capabilities and the same "no solutions" limits.

export interface KbHit {
  kind: string;
  title: string;
  body: string;
  problemSlug: string | null;
  patternId: string | null;
  level: number | null;
  rank?: number;
}

const hitColumns = {
  kind: kbChunks.kind,
  title: kbChunks.title,
  body: kbChunks.body,
  problemSlug: kbChunks.problemSlug,
  patternId: kbChunks.patternId,
  level: kbChunks.level,
};

/**
 * Retrieval (RAG): Postgres full-text search over the knowledge base, ranked by relevance.
 * Words are OR-ed so partial matches still rank, with titles weighted above bodies. Hints are never
 * returned by search, so they can only be revealed one level at a time through getHint.
 * With a problem slug, results are limited to that problem's notes plus general notes.
 */
export async function searchKnowledge(query: string, opts: { slug?: string; limit?: number } = {}): Promise<KbHit[]> {
  const q = query.trim().slice(0, 300);
  if (!q) return [];
  const tsquery = sql`nullif(replace(plainto_tsquery('english', ${q})::text, '&', '|'), '')::tsquery`;
  const rank = sql<number>`ts_rank_cd(${kbChunks.searchVector}, ${tsquery})`;
  return db
    .select({ ...hitColumns, rank })
    .from(kbChunks)
    .where(
      and(
        sql`${kbChunks.searchVector} @@ ${tsquery}`,
        ne(kbChunks.kind, "hint"),
        opts.slug ? or(eq(kbChunks.problemSlug, opts.slug), isNull(kbChunks.problemSlug)) : undefined,
      ),
    )
    .orderBy(sql`${rank} desc`)
    .limit(Math.min(opts.limit ?? 3, 10));
}

/** Hint number `level` (1–3) for a problem, or null if there's no such hint. */
export async function getHint(slug: string, level: number): Promise<KbHit | null> {
  const [hit] = await db
    .select(hitColumns)
    .from(kbChunks)
    .where(and(eq(kbChunks.kind, "hint"), eq(kbChunks.problemSlug, slug), eq(kbChunks.level, level)))
    .limit(1);
  return hit ?? null;
}

export const HINT_LEVELS = 3;

/** A problem's notes of one kind: its key idea, target complexity, or common mistakes. */
export async function getProblemNotes(slug: string, kind: "insight" | "complexity" | "pitfall"): Promise<KbHit[]> {
  return db
    .select(hitColumns)
    .from(kbChunks)
    .where(and(eq(kbChunks.kind, kind), eq(kbChunks.problemSlug, slug)))
    .orderBy(asc(kbChunks.id));
}

/** The roadmap pattern a problem belongs to, with its explanation. */
export async function getPatternForProblem(slug: string): Promise<(KbHit & { id: string }) | null> {
  const [row] = await db.select({ patternId: problems.patternId }).from(problems).where(eq(problems.slug, slug)).limit(1);
  const pattern = row ? patterns.find((p) => p.id === row.patternId) : undefined;
  if (!pattern) return null;
  const [hit] = await db
    .select(hitColumns)
    .from(kbChunks)
    .where(and(eq(kbChunks.kind, "pattern"), eq(kbChunks.patternId, pattern.id)))
    .limit(1);
  return hit ? { ...hit, id: pattern.id } : null;
}

export async function getPattern(id: string): Promise<KbHit | null> {
  const [hit] = await db
    .select(hitColumns)
    .from(kbChunks)
    .where(and(eq(kbChunks.kind, "pattern"), eq(kbChunks.patternId, id)))
    .limit(1);
  return hit ?? null;
}

/**
 * Explains an error message or verdict. Known exception names and verdicts match exactly;
 * anything else falls back to searching the error guides.
 */
export async function explainError(text: string): Promise<KbHit[]> {
  const lower = text.toLowerCase();
  // Most specific first, so "IndexError" beats the generic "None" guide.
  const exact = errorGuides.filter((g) => g.id !== "none-type" && g.match.some((m) => lower.includes(m)));
  const noneMatch = /nonetype|'none'|none\b.*(attribute|subscriptable|iterable)/.test(lower);
  const matched = [...exact, ...(noneMatch ? errorGuides.filter((g) => g.id === "none-type") : [])];
  if (matched.length) {
    return matched.slice(0, 2).map((g) => ({
      kind: "error",
      title: g.title,
      body: g.body,
      problemSlug: null,
      patternId: g.id,
      level: null,
    }));
  }
  const tsquery = sql`nullif(replace(plainto_tsquery('english', ${text.slice(0, 300)})::text, '&', '|'), '')::tsquery`;
  return db
    .select(hitColumns)
    .from(kbChunks)
    .where(and(eq(kbChunks.kind, "error"), sql`${kbChunks.searchVector} @@ ${tsquery}`))
    .orderBy(sql`ts_rank_cd(${kbChunks.searchVector}, ${tsquery}) desc`)
    .limit(2);
}
