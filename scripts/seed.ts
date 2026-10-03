// Loads every problem (src/lib/problems.ts + the content/ catalog) and the tutor knowledge base into the database.
// Safe to re-run: problems are upserted by id, their test cases replaced, all in one transaction, in batches.
// Submissions are untouched. Run with: npm run db:seed   (npm run verify:problems first)
import { Pool } from "@neondatabase/serverless";
import { inArray, notInArray, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/neon-serverless";
import { patterns } from "../src/lib/roadmap.ts";
import { errorGuides, patternNotes } from "../src/lib/tutor/knowledge.ts";
import * as schema from "../src/db/schema.ts";
import { loadAllProblems } from "./catalog.ts";

process.loadEnvFile(".env.local");

const all = loadAllProblems();
console.log(`built ${all.length} problems (${all.reduce((n, p) => n + p.tests.length, 0)} tests)`);

const chunked = <T,>(items: T[], size: number) =>
  Array.from({ length: Math.ceil(items.length / size) }, (_, i) => items.slice(i * size, (i + 1) * size));

const pool = new Pool({ connectionString: process.env.DATABASE_URL_UNPOOLED });
const db = drizzle({ client: pool, schema });

try {
  await db.transaction(async (tx) => {
    const rows = all.map((p) => ({
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
      argTypes: p.argTypes ?? null,
      returnType: p.returnType ?? null,
      outArg: p.outArg ?? null,
      design: p.design ?? false,
      patternId: p.pattern,
    }));
    const excluded = (col: string) => sql.raw(`excluded.${col}`);
    for (const batch of chunked(rows, 100)) {
      await tx
        .insert(schema.problems)
        .values(batch)
        .onConflictDoUpdate({
          target: schema.problems.id,
          set: {
            slug: excluded("slug"),
            title: excluded("title"),
            difficulty: excluded("difficulty"),
            tags: excluded("tags"),
            description: excluded("description"),
            examples: excluded("examples"),
            constraints: excluded("constraints"),
            functionName: excluded("function_name"),
            params: excluded("params"),
            starterCode: excluded("starter_code"),
            compare: excluded("compare"),
            argTypes: excluded("arg_types"),
            returnType: excluded("return_type"),
            outArg: excluded("out_arg"),
            design: excluded("design"),
            patternId: excluded("pattern_id"),
            updatedAt: sql`now()`,
          },
        });
    }
    console.log(`✓ upserted ${rows.length} problems`);

    const ids = all.map((p) => p.id);
    for (const batch of chunked(ids, 1000)) {
      await tx.delete(schema.testCases).where(inArray(schema.testCases.problemId, batch));
    }
    const testRows = all.flatMap((p) =>
      p.tests.map((t, position) => ({
        problemId: p.id,
        position,
        args: t.args,
        expected: t.expected,
        isSample: t.sample ?? false,
      })),
    );
    for (const batch of chunked(testRows, 1000)) await tx.insert(schema.testCases).values(batch);
    console.log(`✓ ${testRows.length} test cases`);

    // Tutor knowledge base: rebuilt from scratch each time (it's derived data, nothing references it).
    type Chunk = typeof schema.kbChunks.$inferInsert;
    const chunks: Chunk[] = [];
    for (const p of all) {
      const g = p.guide;
      const base = { problemSlug: p.slug, patternId: p.pattern };
      g.hints.forEach((body, i) => chunks.push({ ...base, kind: "hint", level: i + 1, title: `${p.title}: hint ${i + 1}`, body }));
      chunks.push({ ...base, kind: "insight", title: `${p.title}: key idea`, body: g.insight });
      chunks.push({
        ...base,
        kind: "complexity",
        title: `${p.title}: target complexity`,
        body: `Aim for ${g.complexity.time} time and ${g.complexity.space} space.${g.complexity.note ? ` ${g.complexity.note}` : ""}`,
      });
      g.pitfalls.forEach((body) => chunks.push({ ...base, kind: "pitfall", title: `${p.title}: common mistake`, body }));
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
    for (const batch of chunked(chunks, 1000)) await tx.insert(schema.kbChunks).values(batch);
    console.log(`✓ tutor knowledge base (${chunks.length} chunks)`);
  });

  // Problems no longer defined anywhere are reported, not deleted, since deleting would also delete submissions.
  const extra = await db
    .select({ id: schema.problems.id, title: schema.problems.title })
    .from(schema.problems)
    .where(notInArray(schema.problems.id, all.map((p) => p.id)));
  for (const p of extra) console.warn(`! ${p.id}. ${p.title} is in the database but no longer defined`);

  console.log(`\nSeeded ${all.length} problems.`);
} finally {
  await pool.end();
}
