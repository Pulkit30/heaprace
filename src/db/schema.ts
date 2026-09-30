// Database schema. Change it here, then run `npm run db:generate` and `npm run db:migrate`.
// Users live in the `neon_auth` schema, which Neon Auth manages; user_id columns hold neon_auth.user.id.
// Keep this file free of extensionless relative imports so scripts can load it directly with Node.
import { sql } from "drizzle-orm";
import {
  boolean,
  customType,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  primaryKey,
  serial,
  text,
  timestamp,
  uniqueIndex,
} from "drizzle-orm/pg-core";

export const difficultyEnum = pgEnum("difficulty", ["Easy", "Medium", "Hard"]);
export const compareModeEnum = pgEnum("compare_mode", ["exact", "unordered", "unordered-deep"]);
export const verdictEnum = pgEnum("verdict", ["Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded"]);
export const raceStatusEnum = pgEnum("race_status", ["lobby", "running", "finished"]);

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
  /** Per argument: "ListNode" / "TreeNode" to build from JSON, or null. Null column = plain JSON args. */
  argTypes: text("arg_types").array().$type<("ListNode" | "TreeNode" | null)[]>(),
  /** "ListNode" / "TreeNode" when the solution returns a node. */
  returnType: text("return_type").$type<"ListNode" | "TreeNode">(),
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
    /** Set when the submission was made during a race. */
    raceRoomId: integer("race_room_id").references(() => raceRooms.id, { onDelete: "set null" }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index("submissions_user_problem_idx").on(t.userId, t.problemId, t.createdAt),
    index("submissions_user_created_idx").on(t.userId, t.createdAt),
  ],
);

export const raceRooms = pgTable(
  "race_rooms",
  {
    id: serial("id").primaryKey(),
    /** Short join code shown to players, e.g. "X7K2QP". */
    code: text("code").notNull().unique(),
    hostId: text("host_id").notNull(),
    /** Chosen when the room is created, revealed only when the race starts. */
    problemId: integer("problem_id")
      .notNull()
      .references(() => problems.id, { onDelete: "cascade" }),
    /** The difficulty the host picked, or null for any. */
    difficulty: difficultyEnum("difficulty"),
    durationSec: integer("duration_sec").notNull(),
    status: raceStatusEnum("status").notNull().default("lobby"),
    /** Start of the race, after the countdown. */
    startsAt: timestamp("starts_at", { withTimezone: true }),
    endsAt: timestamp("ends_at", { withTimezone: true }),
    finishedAt: timestamp("finished_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index("race_rooms_host_idx").on(t.hostId)],
);

export const raceParticipants = pgTable(
  "race_participants",
  {
    roomId: integer("room_id")
      .notNull()
      .references(() => raceRooms.id, { onDelete: "cascade" }),
    userId: text("user_id").notNull(),
    /** Display name at join time. */
    name: text("name").notNull(),
    joinedAt: timestamp("joined_at", { withTimezone: true }).notNull().defaultNow(),
    /** When this player's first Accepted submission landed. */
    solvedAt: timestamp("solved_at", { withTimezone: true }),
    attempts: integer("attempts").notNull().default(0),
  },
  (t) => [primaryKey({ columns: [t.roomId, t.userId] }), index("race_participants_user_idx").on(t.userId)],
);

/** Postgres full-text search vector. */
const tsvector = customType<{ data: string }>({ dataType: () => "tsvector" });

/**
 * The tutor's knowledge base (RAG): hints, key ideas, complexity targets, pitfalls, pattern notes and
 * error guides, loaded from src/lib/tutor/knowledge.ts by `npm run db:seed`. Searched with full-text search.
 */
export const kbChunks = pgTable(
  "kb_chunks",
  {
    id: serial("id").primaryKey(),
    /** hint | insight | complexity | pitfall | pattern | error */
    kind: text("kind").notNull(),
    problemSlug: text("problem_slug"),
    patternId: text("pattern_id"),
    /** Hint order (1–3) for kind = "hint". */
    level: integer("level"),
    title: text("title").notNull(),
    body: text("body").notNull(),
    /** Title weighted above body, kept in sync by Postgres. */
    searchVector: tsvector("search_vector").generatedAlwaysAs(
      sql`setweight(to_tsvector('english', coalesce(title, '')), 'A') || setweight(to_tsvector('english', coalesce(body, '')), 'B')`,
    ),
  },
  (t) => [
    index("kb_chunks_search_idx").using("gin", t.searchVector),
    index("kb_chunks_problem_idx").on(t.problemSlug, t.kind, t.level),
  ],
);
