// Pure date and streak helpers. Days are "YYYY-MM-DD" strings in the user's timezone.
// No imports, so scripts/test-streak.ts can load this file directly with Node.

export interface DayActivity {
  day: string;
  submissions: number;
  accepted: number;
}

export interface StreakSummary {
  /** Consecutive days with an Accepted submission, ending today (or yesterday if nothing is solved yet today). */
  current: number;
  longest: number;
  solvedToday: boolean;
}

const MS_PER_DAY = 86_400_000;

const toUtcMs = (day: string) => Date.parse(`${day}T00:00:00Z`);
const fromUtcMs = (ms: number) => new Date(ms).toISOString().slice(0, 10);

export function addDays(day: string, n: number): string {
  return fromUtcMs(toUtcMs(day) + n * MS_PER_DAY);
}

/** 0 = Sunday ... 6 = Saturday. */
export function weekday(day: string): number {
  return new Date(toUtcMs(day)).getUTCDay();
}

/** Today's date in a timezone, e.g. "2026-09-29" for Asia/Kolkata. */
export function todayIn(timeZone: string, now = new Date()): string {
  // en-CA formats as YYYY-MM-DD.
  return new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
}

export function computeStreaks(activity: DayActivity[], today: string): StreakSummary {
  const solvedDays = new Set(activity.filter((a) => a.accepted > 0).map((a) => a.day));
  const solvedToday = solvedDays.has(today);

  // An unsolved today doesn't break the streak yet: count back from yesterday instead.
  let current = 0;
  for (let d = solvedToday ? today : addDays(today, -1); solvedDays.has(d); d = addDays(d, -1)) current++;

  let longest = 0;
  let run = 0;
  let prev: string | null = null;
  for (const day of [...solvedDays].sort()) {
    run = prev !== null && addDays(prev, 1) === day ? run + 1 : 1;
    longest = Math.max(longest, run);
    prev = day;
  }

  return { current, longest: Math.max(longest, current), solvedToday };
}
