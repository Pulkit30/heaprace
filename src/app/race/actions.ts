"use server";

import { and, count, eq, isNull, sql } from "drizzle-orm";
import { redirect } from "next/navigation";
import { db } from "@/db";
import { problems, raceParticipants, raceRooms } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth/server";
import type { Difficulty } from "@/lib/problems";
import { getProblem } from "@/lib/queries";
import {
  COUNTDOWN_SEC,
  DURATIONS_MIN,
  finishIfDone,
  generateCode,
  getRoomByCode,
  MAX_PARTICIPANTS,
  normalizeCode,
  phaseOf,
  pickProblemId,
} from "@/lib/race";
import { judgeAndRecord, type SubmitResult } from "@/lib/submit";

export type RaceFormState = { error: string } | null;

const DIFFICULTIES: Difficulty[] = ["Easy", "Medium", "Hard"];

async function requireUser(next: string) {
  const user = await getCurrentUser();
  if (!user) redirect(`/auth/sign-in?next=${encodeURIComponent(next)}`);
  return user;
}

export async function createRace(_prev: RaceFormState, formData: FormData): Promise<RaceFormState> {
  const user = await requireUser("/race");
  const rawDifficulty = String(formData.get("difficulty") ?? "any");
  const difficulty = DIFFICULTIES.includes(rawDifficulty as Difficulty) ? (rawDifficulty as Difficulty) : null;
  const minutes = Number(formData.get("duration"));
  if (!DURATIONS_MIN.includes(minutes as (typeof DURATIONS_MIN)[number])) return { error: "Pick a race length." };

  const problemId = await pickProblemId(difficulty);
  if (problemId === null) return { error: "No problems match that difficulty yet." };

  // Codes are random; retry on the rare collision.
  for (let attempt = 0; attempt < 5; attempt++) {
    const code = generateCode();
    const [room] = await db
      .insert(raceRooms)
      .values({ code, hostId: user.id, problemId, difficulty, durationSec: minutes * 60 })
      .onConflictDoNothing({ target: raceRooms.code })
      .returning({ id: raceRooms.id });
    if (!room) continue;
    await db.insert(raceParticipants).values({ roomId: room.id, userId: user.id, name: user.name || "Host" });
    redirect(`/race/${code}`);
  }
  return { error: "Couldn't create a room. Try again." };
}

export async function joinRace(_prev: RaceFormState, formData: FormData): Promise<RaceFormState> {
  const code = normalizeCode(formData.get("code"));
  if (!code) return { error: "Room codes are 6 letters and numbers." };
  const user = await requireUser(`/race/${code}`);

  const room = await getRoomByCode(code);
  if (!room) return { error: "No race with that code." };

  const [already] = await db
    .select({ userId: raceParticipants.userId })
    .from(raceParticipants)
    .where(and(eq(raceParticipants.roomId, room.id), eq(raceParticipants.userId, user.id)));
  if (!already) {
    if (room.status !== "lobby") return { error: "That race has already started." };
    const [{ n }] = await db.select({ n: count() }).from(raceParticipants).where(eq(raceParticipants.roomId, room.id));
    if (n >= MAX_PARTICIPANTS) return { error: `That room is full (${MAX_PARTICIPANTS} players).` };
    await db
      .insert(raceParticipants)
      .values({ roomId: room.id, userId: user.id, name: user.name || "Player" })
      .onConflictDoNothing();
  }
  redirect(`/race/${code}`);
}

export async function startRace(code: string): Promise<{ error?: string }> {
  const user = await getCurrentUser();
  const c = normalizeCode(code);
  if (!user || !c) return { error: "Not allowed." };
  const room = await getRoomByCode(c);
  if (!room || room.hostId !== user.id) return { error: "Only the host can start the race." };
  if (room.status !== "lobby") return {};

  await db
    .update(raceRooms)
    .set({
      status: "running",
      startsAt: sql`now() + make_interval(secs => ${COUNTDOWN_SEC})`,
      endsAt: sql`now() + make_interval(secs => ${COUNTDOWN_SEC + room.durationSec})`,
    })
    .where(and(eq(raceRooms.id, room.id), eq(raceRooms.status, "lobby")));
  return {};
}

export async function cancelRace(code: string): Promise<void> {
  const user = await getCurrentUser();
  const c = normalizeCode(code);
  if (user && c) {
    await db
      .delete(raceRooms)
      .where(and(eq(raceRooms.code, c), eq(raceRooms.hostId, user.id), eq(raceRooms.status, "lobby")));
  }
  redirect("/race");
}

export async function leaveRace(code: string): Promise<void> {
  const user = await getCurrentUser();
  const c = normalizeCode(code);
  const room = c ? await getRoomByCode(c) : null;
  if (user && room && room.status === "lobby" && room.hostId !== user.id) {
    await db
      .delete(raceParticipants)
      .where(and(eq(raceParticipants.roomId, room.id), eq(raceParticipants.userId, user.id)));
  }
  redirect("/race");
}

/** Race submit: same server judge as practice, but only while the race is running, and it updates the standings. */
export async function submitRaceSolution(code: string, source: string): Promise<SubmitResult> {
  const user = await getCurrentUser();
  if (!user) return { ok: false, reason: "signed-out", message: "Sign in to submit." };
  const c = normalizeCode(code);
  const room = c ? await getRoomByCode(c) : null;
  if (!room) return { ok: false, reason: "invalid", message: "Race not found." };
  if (phaseOf(await finishIfDone(room)) !== "running") {
    return { ok: false, reason: "race-closed", message: "The race isn't running, so submissions are closed." };
  }

  const [me] = await db
    .select()
    .from(raceParticipants)
    .where(and(eq(raceParticipants.roomId, room.id), eq(raceParticipants.userId, user.id)));
  if (!me) return { ok: false, reason: "invalid", message: "You're not in this race." };

  const [p] = await db.select({ slug: problems.slug }).from(problems).where(eq(problems.id, room.problemId));
  const problem = p ? await getProblem(p.slug) : null;
  if (!problem) return { ok: false, reason: "invalid", message: "Problem not found." };

  const res = await judgeAndRecord({ userId: user.id, problem, code: source, raceRoomId: room.id });
  if (!res.ok) return res;

  // Count the attempt; the first Accepted sets the finish time (the judge's clock, not the browser's).
  await db
    .update(raceParticipants)
    .set({ attempts: sql`${raceParticipants.attempts} + 1` })
    .where(and(eq(raceParticipants.roomId, room.id), eq(raceParticipants.userId, user.id)));
  if (res.result.verdict === "Accepted") {
    await db
      .update(raceParticipants)
      .set({ solvedAt: sql`now()` })
      .where(
        and(
          eq(raceParticipants.roomId, room.id),
          eq(raceParticipants.userId, user.id),
          isNull(raceParticipants.solvedAt),
        ),
      );
    await finishIfDone(room);
  }
  return res;
}
