"use client";

import Link from "next/link";
import { useState } from "react";
import { addDays, weekday, type DayActivity, type StreakSummary } from "@/lib/streak";

const WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];

const monthName = (ym: string) =>
  new Date(`${ym}-01T00:00:00Z`).toLocaleDateString("en-US", { timeZone: "UTC", month: "long", year: "numeric" });

function shiftMonth(ym: string, delta: number): string {
  const [y, m] = ym.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return d.toISOString().slice(0, 7);
}

interface Props {
  activity: DayActivity[];
  today: string;
  streak: StreakSummary;
}

/** LeetCode-style sidebar calendar: one month at a time, solved days in green. */
export default function MonthCalendar({ activity, today, streak }: Props) {
  const thisMonth = today.slice(0, 7);
  const [month, setMonth] = useState(thisMonth);
  const byDay = new Map(activity.map((a) => [a.day, a]));

  const first = `${month}-01`;
  const daysInMonth = Number(addDays(`${shiftMonth(month, 1)}-01`, -1).slice(8, 10));
  const cells: (string | null)[] = [
    ...Array<null>(weekday(first)).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => addDays(first, i)),
  ];
  const solvedThisMonth = cells.filter((d) => d && (byDay.get(d)?.accepted ?? 0) > 0).length;

  const navButton =
    "flex h-7 w-7 items-center justify-center rounded-md text-muted transition-colors hover:bg-surface-2 hover:text-fg disabled:opacity-30 disabled:hover:bg-transparent";

  return (
    <div className="rounded-lg border border-line bg-surface p-4">
      <Link href="/progress" className="flex items-center gap-3 rounded-md hover:opacity-80">
        <span className={`text-2xl ${streak.solvedToday ? "" : "opacity-50 grayscale"}`} aria-hidden="true">
          🔥
        </span>
        <span>
          <span className="block text-sm font-semibold">
            {streak.current} day{streak.current === 1 ? "" : "s"} streak
          </span>
          <span className="block text-xs text-muted">
            {streak.solvedToday
              ? "Solved today. Nice work!"
              : streak.current > 0
                ? "Solve one today to keep it going"
                : "Solve a problem to start a streak"}
          </span>
        </span>
      </Link>

      <div className="mt-4 flex items-center justify-between">
        <button onClick={() => setMonth(shiftMonth(month, -1))} className={navButton} aria-label="Previous month">
          ‹
        </button>
        <span className="text-sm font-medium">{monthName(month)}</span>
        <button
          onClick={() => setMonth(shiftMonth(month, 1))}
          disabled={month >= thisMonth}
          className={navButton}
          aria-label="Next month"
        >
          ›
        </button>
      </div>

      <div className="mt-2 grid grid-cols-7 gap-1 text-center">
        {WEEKDAYS.map((d, i) => (
          <span key={i} className="py-1 text-[11px] text-muted">
            {d}
          </span>
        ))}
        {cells.map((day, i) => {
          if (!day) return <span key={`blank-${i}`} />;
          const a = byDay.get(day);
          const solved = (a?.accepted ?? 0) > 0;
          const attempted = !solved && (a?.submissions ?? 0) > 0;
          const future = day > today;
          const title = a
            ? `${a.submissions} submission${a.submissions === 1 ? "" : "s"}${a.accepted ? `, ${a.accepted} accepted` : ""}`
            : undefined;
          return (
            <span
              key={day}
              title={title}
              className={`relative mx-auto flex h-8 w-8 items-center justify-center rounded-full text-xs ${
                solved ? "bg-easy font-semibold text-white" : future ? "text-muted/50" : "text-fg"
              } ${day === today ? "ring-2 ring-accent-fill ring-offset-1 ring-offset-surface" : ""}`}
            >
              {Number(day.slice(8, 10))}
              {attempted && <span className="absolute bottom-1 h-1 w-1 rounded-full bg-medium" aria-hidden="true" />}
            </span>
          );
        })}
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-line pt-3 text-xs text-muted">
        <span>
          {solvedThisMonth} day{solvedThisMonth === 1 ? "" : "s"} solved this month
        </span>
        <span className="flex items-center gap-2">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-easy" /> solved
          </span>
          <span className="flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-medium" /> tried
          </span>
        </span>
      </div>
    </div>
  );
}
