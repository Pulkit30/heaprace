// Loads the problems in src/lib/problems.ts into the database. Safe to re-run after editing problems:
// each problem is upserted and its test cases replaced, in one transaction. Submissions are untouched.
// Run with: npm run db:seed   (run npm run verify:problems first)
import { Pool } from "@neondatabase/serverless";
import { eq, notInArray, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/neon-serverless";
import { problems as problemData } from "../src/lib/problems.ts";
import { patterns } from "../src/lib/roadmap.ts";
import { errorGuides, patternNotes, problemGuides } from "../src/lib/tutor/knowledge.ts";
import * as schema from "../src/db/schema.ts";

process.loadEnvFile(".env.local");
const pool = new Pool({ connectionString: process.env.DATABASE_URL_UNPOOLED });
const db = drizzle({ client: pool, schema });

try {
  await db.transaction(async (tx) => {
    for (const { tests, ...p } of problemData) {
      const row = {
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
        argTypes: p.argTypes ?? null,
        returnType: p.returnType ?? null,
      };
      await tx
        .insert(schema.problems)
        .values({ id: p.id, ...row })
        .onConflictDoUpdate({ target: schema.problems.id, set: { ...row, updatedAt: sql`now()` } });

      await tx.delete(schema.testCases).where(eq(schema.testCases.problemId, p.id));
      await tx.insert(schema.testCases).values(
        tests.map((t, position) => ({
          problemId: p.id,
          position,
          args: t.args,
          expected: t.expected,
          isSample: t.sample ?? false,
        })),
      );
      console.log(`✓ ${p.id}. ${p.title} (${tests.length} tests)`);
    }

    // Tutor knowledge base: rebuilt from scratch each time (it's derived data, nothing references it).
    type Chunk = typeof schema.kbChunks.$inferInsert;
    const titleOf = new Map(problemData.map((p) => [p.slug, p.title]));
    const patternOf = new Map(patterns.flatMap((pat) => pat.problems.map((slug) => [slug, pat.id] as const)));
    const chunks: Chunk[] = [];
    for (const g of problemGuides) {
      const base = { problemSlug: g.slug, patternId: patternOf.get(g.slug) ?? null };
      const title = titleOf.get(g.slug) ?? g.slug;
      g.hints.forEach((body, i) => chunks.push({ ...base, kind: "hint", level: i + 1, title: `${title}: hint ${i + 1}`, body }));
      chunks.push({ ...base, kind: "insight", title: `${title}: key idea`, body: g.insight });
      chunks.push({
        ...base,
        kind: "complexity",
        title: `${title}: target complexity`,
        body: `Aim for ${g.complexity.time} time and ${g.complexity.space} space.${g.complexity.note ? ` ${g.complexity.note}` : ""}`,
      });
      g.pitfalls.forEach((body) => chunks.push({ ...base, kind: "pitfall", title: `${title}: common mistake`, body }));
    }
    for (const pat of patterns) {
      const note = patternNotes.find((n) => n.patternId === pat.id);
      chunks.push({
        kind: "pattern",
        patternId: pat.id,
        title: pat.name,
        body: [pat.summary, `Use it when: ${pat.useWhen}`, note?.howTo, note && `Watch out for: ${note.pitfalls}`]
          .filter(Boolean)
          .join(" "),
      });
    }
    for (const e of errorGuides) chunks.push({ kind: "error", patternId: e.id, title: e.title, body: e.body });

    await tx.delete(schema.kbChunks);
    await tx.insert(schema.kbChunks).values(chunks);
    console.log(`✓ tutor knowledge base (${chunks.length} chunks)`);
  });

  // Problems removed from problems.ts are reported, not deleted, since deleting would also delete submissions.
  const extra = await db
    .select({ id: schema.problems.id, title: schema.problems.title })
    .from(schema.problems)
    .where(notInArray(schema.problems.id, problemData.map((p) => p.id)));
  for (const p of extra) console.warn(`! ${p.id}. ${p.title} is in the database but not in problems.ts`);

  console.log(`\nSeeded ${problemData.length} problems.`);
} finally {
  await pool.end();
}
