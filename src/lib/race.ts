import "server-only";
import { randomInt } from "node:crypto";
import { and, asc, eq, inArray, sql } from "drizzle-orm";
import { db } from "@/db";
import { problems, raceParticipants, raceRooms } from "@/db/schema";
import type { Difficulty, Problem } from "./problems";
import { getProblem } from "./queries";

export const MAX_PARTICIPANTS = 8;
export const COUNTDOWN_SEC = 5;
export const DURATIONS_MIN = [10, 20, 30, 45] as const;

// No 0/O or 1/I, so codes are easy to read aloud.
const CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
export const CODE_LENGTH = 6;

export function generateCode(): string {
  return Array.from({ length: CODE_LENGTH }, () => CODE_ALPHABET[randomInt(CODE_ALPHABET.length)]).join("");
}

export function normalizeCode(code: unknown): string | null {
  if (typeof code !== "string") return null;
  const c = code.trim().toUpperCase();
  return c.length === CODE_LENGTH && [...c].every((ch) => CODE_ALPHABET.includes(ch)) ? c : null;
}

export type RacePhase = "lobby" | "countdown" | "running" | "finished";

export interface RaceParticipantView {
  userId: string;
  name: string;
  isHost: boolean;
  attempts: number;
  solvedAt: string | null;
  /** Time from race start to first Accepted. */
  solveMs: number | null;
  /** 1-based finishing position, or null if not solved. */
  rank: number | null;
}

export interface RaceState {
  code: string;
  /** The viewer's user id, to highlight "you" in the standings. */
  youId: string;
  phase: RacePhase;
  isHost: boolean;
  isParticipant: boolean;
  difficulty: Difficulty | null;
  durationSec: number;
  startsAt: string | null;
  endsAt: string | null;
  /** Server clock, so browsers can correct for their own clock being off. */
  serverNow: string;
  participants: RaceParticipantView[];
  maxParticipants: number;
  /** For participants once the race has started: the problem with sample tests only. */
  problem: Problem | null;
  /** Revealed to everyone after the race. */
  revealedProblem: { slug: string; title: string; difficulty: Difficulty } | null;
}

type RoomRow = typeof raceRooms.$inferSelect;

export async function getRoomByCode(code: string): Promise<RoomRow | null> {
  const [room] = await db.select().from(raceRooms).where(eq(raceRooms.code, code)).limit(1);
  return room ?? null;
}

export function phaseOf(room: RoomRow, now = new Date()): RacePhase {
  if (room.status === "lobby") return "lobby";
  if (room.status === "finished") return "finished";
  if (room.startsAt && now < room.startsAt) return "countdown";
  if (room.endsAt && now >= room.endsAt) return "finished";
  return "running";
}

/** Marks a running race finished once time is up or every player has solved it. */
export async function finishIfDone(room: RoomRow): Promise<RoomRow> {
  if (room.status !== "running") return room;
  const now = new Date();
  let done = !!room.endsAt && now >= room.endsAt;
  if (!done) {
    const [{ total, solved }] = await db
      .select({
        total: sql<number>`count(*)::int`,
        solved: sql<number>`(count(*) filter (where ${raceParticipants.solvedAt} is not null))::int`,
      })
      .from(raceParticipants)
      .where(eq(raceParticipants.roomId, room.id));
    done = total > 0 && solved === total;
  }
  if (!done) return room;
  const [updated] = await db
    .update(raceRooms)
    .set({ status: "finished", finishedAt: sql`least(now(), ${raceRooms.endsAt})` })
    .where(and(eq(raceRooms.id, room.id), eq(raceRooms.status, "running")))
    .returning();
  return updated ?? { ...room, status: "finished" };
}

export async function pickProblemId(difficulty: Difficulty | null): Promise<number | null> {
  const [row] = await db
    .select({ id: problems.id })
    .from(problems)
    .where(difficulty ? eq(problems.difficulty, difficulty) : undefined)
    .orderBy(sql`random()`)
    .limit(1);
  return row?.id ?? null;
}

export async function getRaceState(code: string, userId: string): Promise<RaceState | null> {
  let room = await getRoomByCode(code);
  if (!room) return null;
  room = await finishIfDone(room);
  const now = new Date();
  const phase = phaseOf(room, now);

  const rows = await db
    .select()
    .from(raceParticipants)
    .where(eq(raceParticipants.roomId, room.id))
    .orderBy(asc(raceParticipants.joinedAt));

  const startMs = room.startsAt?.getTime() ?? null;
  const solvedOrder = rows
    .filter((r) => r.solvedAt)
    .sort((a, b) => a.solvedAt!.getTime() - b.solvedAt!.getTime())
    .map((r) => r.userId);
  const participants: RaceParticipantView[] = rows
    .map((r) => ({
      userId: r.userId,
      name: r.name,
      isHost: r.userId === room.hostId,
      attempts: r.attempts,
      solvedAt: r.solvedAt?.toISOString() ?? null,
      solveMs: r.solvedAt && startMs !== null ? r.solvedAt.getTime() - startMs : null,
      rank: r.solvedAt ? solvedOrder.indexOf(r.userId) + 1 : null,
    }))
    .sort((a, b) => (a.rank ?? Infinity) - (b.rank ?? Infinity));

  const isParticipant = rows.some((r) => r.userId === userId);
  const started = phase === "running" || phase === "finished";

  let problem: Problem | null = null;
  let revealedProblem: RaceState["revealedProblem"] = null;
  if (started) {
    const [p] = await db
      .select({ slug: problems.slug, title: problems.title, difficulty: problems.difficulty })
      .from(problems)
      .where(eq(problems.id, room.problemId))
      .limit(1);
    if (p && isParticipant) {
      const full = await getProblem(p.slug);
      if (full) problem = { ...full, tests: full.tests.filter((t) => t.sample) };
    }
    if (p && phase === "finished") revealedProblem = p;
  }

  return {
    code: room.code,
    youId: userId,
    phase,
    isHost: room.hostId === userId,
    isParticipant,
    difficulty: room.difficulty,
    durationSec: room.durationSec,
    startsAt: room.startsAt?.toISOString() ?? null,
    endsAt: room.endsAt?.toISOString() ?? null,
    serverNow: now.toISOString(),
    participants,
    maxParticipants: MAX_PARTICIPANTS,
    problem,
    revealedProblem,
  };
}

export interface RecentRace {
  code: string;
  phase: RacePhase;
  players: number;
  rank: number | null;
  createdAt: string;
}

/** The user's latest races, newest first. */
export async function getRecentRaces(userId: string, limit = 10): Promise<RecentRace[]> {
  const mine = await db
    .select({ room: raceRooms, solvedAt: raceParticipants.solvedAt })
    .from(raceParticipants)
    .innerJoin(raceRooms, eq(raceRooms.id, raceParticipants.roomId))
    .where(eq(raceParticipants.userId, userId))
    .orderBy(sql`${raceRooms.createdAt} desc`)
    .limit(limit);
  if (mine.length === 0) return [];

  const everyone = await db
    .select({ roomId: raceParticipants.roomId, solvedAt: raceParticipants.solvedAt })
    .from(raceParticipants)
    .where(inArray(raceParticipants.roomId, mine.map((m) => m.room.id)));

  return mine.map(({ room, solvedAt }) => {
    const players = everyone.filter((p) => p.roomId === room.id);
    const rank = solvedAt
      ? 1 + players.filter((p) => p.solvedAt && p.solvedAt.getTime() < solvedAt.getTime()).length
      : null;
    return {
      code: room.code,
      phase: phaseOf(room),
      players: players.length,
      rank,
      createdAt: room.createdAt.toISOString(),
    };
  });
}

/** Races played and won, for profiles. */
export async function getRaceStats(userId: string): Promise<{ played: number; wins: number }> {
  const [row] = await db.execute<{ played: number; wins: number }>(sql`
    select
      count(*)::int as played,
      count(*) filter (
        where p.solved_at is not null
          and p.solved_at = (select min(q.solved_at) from ${raceParticipants} q where q.room_id = p.room_id)
      )::int as wins
    from ${raceParticipants} p
    join ${raceRooms} r on r.id = p.room_id
    where p.user_id = ${userId} and r.status <> 'lobby'
  `).then((r) => r.rows);
  return { played: Number(row?.played ?? 0), wins: Number(row?.wins ?? 0) };
}
