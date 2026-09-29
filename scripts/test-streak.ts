// Tests for src/lib/streak.ts. Run with: npm run test:streak
import assert from "node:assert/strict";
import { test } from "node:test";
import { addDays, computeStreaks, todayIn, weekday, type DayActivity } from "../src/lib/streak.ts";

const solved = (...days: string[]): DayActivity[] => days.map((day) => ({ day, submissions: 1, accepted: 1 }));

test("date helpers cross month and year boundaries", () => {
  assert.equal(addDays("2026-02-28", 1), "2026-03-01");
  assert.equal(addDays("2026-01-01", -1), "2025-12-31");
  assert.equal(addDays("2028-02-28", 1), "2028-02-29"); // leap year
  assert.equal(weekday("2026-09-27"), 0); // a Sunday
});

test("no activity means no streak", () => {
  assert.deepEqual(computeStreaks([], "2026-09-29"), { current: 0, longest: 0, solvedToday: false });
});

test("streak includes today when solved today", () => {
  const s = computeStreaks(solved("2026-09-27", "2026-09-28", "2026-09-29"), "2026-09-29");
  assert.deepEqual(s, { current: 3, longest: 3, solvedToday: true });
});

test("unsolved today keeps yesterday's streak alive", () => {
  const s = computeStreaks(solved("2026-09-27", "2026-09-28"), "2026-09-29");
  assert.deepEqual(s, { current: 2, longest: 2, solvedToday: false });
});

test("a missed day breaks the current streak but keeps the longest", () => {
  const s = computeStreaks(solved("2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-28"), "2026-09-30");
  assert.deepEqual(s, { current: 0, longest: 4, solvedToday: false });
});

test("days with only failed submissions don't count", () => {
  const activity: DayActivity[] = [
    { day: "2026-09-28", submissions: 3, accepted: 1 },
    { day: "2026-09-29", submissions: 5, accepted: 0 },
  ];
  assert.deepEqual(computeStreaks(activity, "2026-09-29"), { current: 1, longest: 1, solvedToday: false });
});

test("streaks run across a month boundary", () => {
  const s = computeStreaks(solved("2026-08-30", "2026-08-31", "2026-09-01"), "2026-09-01");
  assert.equal(s.current, 3);
});

test("today depends on the timezone", () => {
  const now = new Date("2026-09-29T20:00:00Z"); // 1:30 AM on the 30th in India
  assert.equal(todayIn("UTC", now), "2026-09-29");
  assert.equal(todayIn("Asia/Kolkata", now), "2026-09-30");
});
