// Loads the problems in src/lib/problems.ts into the database. Safe to re-run after editing problems:
// each problem is upserted and its test cases replaced, in one transaction. Submissions are untouched.
// Run with: npm run db:seed   (run npm run verify:problems first)
import { Pool } from "@neondatabase/serverless";
import { eq, notInArray, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/neon-serverless";
import { problems as problemData } from "../src/lib/problems.ts";
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
