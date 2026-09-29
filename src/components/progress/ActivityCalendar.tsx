import { addDays, weekday, type DayActivity } from "@/lib/streak";

const WEEKS = 53;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// 0 = no submissions; darker green for busier days.
const levelClass = ["bg-surface-2", "bg-easy/30", "bg-easy/55", "bg-easy/80", "bg-easy"];
const level = (n: number) => (n === 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : n <= 6 ? 3 : 4);

function label(day: string, a: DayActivity | undefined) {
  const date = new Date(`${day}T00:00:00Z`).toLocaleDateString("en-US", {
    timeZone: "UTC",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
  if (!a) return `No submissions on ${date}`;
  const subs = `${a.submissions} submission${a.submissions === 1 ? "" : "s"}`;
  return `${subs}${a.accepted ? `, ${a.accepted} accepted` : ""} on ${date}`;
}

/** A year of daily activity: one column per week (Sunday at the top), ending with the current week. */
export default function ActivityCalendar({ activity, today }: { activity: DayActivity[]; today: string }) {
  const byDay = new Map(activity.map((a) => [a.day, a]));
  const start = addDays(today, -((WEEKS - 1) * 7 + weekday(today)));

  const weeks = Array.from({ length: WEEKS }, (_, w) =>
    Array.from({ length: 7 }, (_, d) => addDays(start, w * 7 + d)),
  );
  // Label a column with its month when that month's first day falls in it.
  const monthLabels = weeks.map((days) => {
    const first = days.find((d) => d.endsWith("-01"));
    return first ? MONTHS[Number(first.slice(5, 7)) - 1] : "";
  });

  return (
    <div className="overflow-x-auto pb-1">
      <div className="inline-grid grid-flow-col gap-[3px]" style={{ gridTemplateRows: "auto repeat(7, 11px)" }}>
        {weeks.map((days, w) => (
          <div key={days[0]} className="contents">
            <div className="h-4 w-[11px] overflow-visible whitespace-nowrap text-[10px] leading-4 text-muted">
              {monthLabels[w]}
            </div>
            {days.map((day) => {
              if (day > today) return <div key={day} className="h-[11px] w-[11px]" />;
              const a = byDay.get(day);
              return (
                <div
                  key={day}
                  title={label(day, a)}
                  className={`h-[11px] w-[11px] rounded-[2px] ${levelClass[level(a?.submissions ?? 0)]} ${
                    day === today ? "ring-1 ring-fg/40" : ""
                  }`}
                />
              );
            })}
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-end gap-1.5 text-[11px] text-muted">
        Less
        {levelClass.map((c) => (
          <span key={c} className={`h-[11px] w-[11px] rounded-[2px] ${c}`} />
        ))}
        More
      </div>
    </div>
  );
}
