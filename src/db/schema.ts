// Database schema. Change it here, then run `npm run db:generate` and `npm run db:migrate`.
// Users live in the `neon_auth` schema, which Neon Auth manages; user_id columns hold neon_auth.user.id.
// Keep this file free of extensionless relative imports so scripts can load it directly with Node.
import { boolean, index, integer, jsonb, pgEnum, pgTable, serial, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";

export const difficultyEnum = pgEnum("difficulty", ["Easy", "Medium", "Hard"]);
export const compareModeEnum = pgEnum("compare_mode", ["exact", "unordered", "unordered-deep"]);
export const verdictEnum = pgEnum("verdict", ["Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded"]);

export const problems = pgTable("problems", {
  /** The problem number shown to users (1. Two Sum). */
  id: integer("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  title: text("title").notNull(),
  difficulty: difficultyEnum("difficulty").notNull(),
  tags: text("tags").array().notNull(),
  description: text("description").notNull(),
  examples: jsonb("examples").$type<{ input: string; output: string; explanation?: string }[]>().notNull(),
  constraints: text("constraints").array().notNull(),
  functionName: text("function_name").notNull(),
  params: text("params").array().notNull(),
  starterCode: text("starter_code").notNull(),
  compare: compareModeEnum("compare").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export const testCases = pgTable(
  "test_cases",
  {
    id: serial("id").primaryKey(),
    problemId: integer("problem_id")
      .notNull()
      .references(() => problems.id, { onDelete: "cascade" }),
    /** Order within the problem, starting at 0. */
    position: integer("position").notNull(),
    args: jsonb("args").$type<unknown[]>().notNull(),
    expected: jsonb("expected").notNull(),
    isSample: boolean("is_sample").notNull().default(false),
  },
  (t) => [uniqueIndex("test_cases_problem_position_idx").on(t.problemId, t.position)],
);

export const submissions = pgTable(
  "submissions",
  {
    id: serial("id").primaryKey(),
    userId: text("user_id").notNull(),
    problemId: integer("problem_id")
      .notNull()
      .references(() => problems.id, { onDelete: "cascade" }),
    language: text("language").notNull().default("python"),
    code: text("code").notNull(),
    verdict: verdictEnum("verdict").notNull(),
    passed: integer("passed").notNull(),
    total: integer("total").notNull(),
    runtimeMs: integer("runtime_ms").notNull(),
    /** Position of the first failing test, if any. */
    failedTest: integer("failed_test"),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index("submissions_user_problem_idx").on(t.userId, t.problemId, t.createdAt),
    index("submissions_user_created_idx").on(t.userId, t.createdAt),
  ],
);
