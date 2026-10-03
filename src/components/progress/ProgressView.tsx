import Link from "next/link";
import type { DifficultyProgress } from "@/lib/queries";
import { addDays, type DayActivity, type StreakSummary } from "@/lib/streak";
import ActivityCalendar from "./ActivityCalendar";

const barColor = { Easy: "bg-easy", Medium: "bg-medium", Hard: "bg-hard" } as const;
const textColor = { Easy: "text-easy", Medium: "text-medium", Hard: "text-hard" } as const;

interface Props {
  name: string;
  activity: DayActivity[];
  today: string;
  streak: StreakSummary;
  progress: DifficultyProgress[];
  /** Page heading. Defaults to "My progress". */
  title?: string;
  /** Show links that only make sense for your own page (all submissions). */
  isOwn?: boolean;
  image?: string | null;
  raceStats?: { played: number; wins: number };
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-lg border border-line bg-surface p-4">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}

export default function ProgressView({
  name,
  activity,
  today,
  streak,
  progress,
  title = "My progress",
  isOwn = true,
  image,
  raceStats,
}: Props) {
  const yearAgo = addDays(today, -364);
  const lastYear = activity.filter((a) => a.day >= yearAgo && a.day <= today);
  const yearSubmissions = lastYear.reduce((n, a) => n + a.submissions, 0);
  const solved = progress.reduce((n, p) => n + p.solved, 0);
  const total = progress.reduce((n, p) => n + p.total, 0);
  const days = (n: number) => `${n} day${n === 1 ? "" : "s"}`;

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <div className="flex items-center gap-4">
        {image !== undefined && (
          <span className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-accent-fill text-xl font-semibold text-on-accent">
            {image ? (
              // eslint-disable-next-line @next/next/no-img-element -- avatar from the auth provider's domain
              <img src={image} alt="" className="h-full w-full object-cover" referrerPolicy="no-referrer" />
            ) : (
              name.trim().charAt(0).toUpperCase() || "?"
            )}
          </span>
        )}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-1 text-sm text-muted">{name}</p>
        </div>
      </div>

      <section className="mt-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <div className="rounded-lg border border-line bg-surface p-5">
          <p className="text-xs text-muted">Solved</p>
          <p className="mt-1 text-3xl font-semibold tracking-tight">
            {solved}
            <span className="text-base font-normal text-muted">/{total}</span>
          </p>
          <div className="mt-4 space-y-3">
            {progress.map((p) => (
              <div key={p.difficulty}>
                <div className="flex justify-between text-sm">
                  <span className={textColor[p.difficulty]}>{p.difficulty}</span>
                  <span className="text-muted">
                    <span className="text-fg">{p.solved}</span>/{p.total}
                  </span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-surface-2">
                  <div
                    className={`h-full rounded-full ${barColor[p.difficulty]}`}
                    style={{ width: `${p.total ? (p.solved / p.total) * 100 : 0}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat
            label="Current streak"
            value={`🔥 ${days(streak.current)}`}
            hint={streak.solvedToday ? "Solved today ✓" : streak.current > 0 ? "Solve one today to keep it" : "Solve a problem to start"}
          />
          <Stat label="Longest streak" value={days(streak.longest)} />
          <Stat label="Active days" value={String(lastYear.length)} hint="in the past year" />
          {raceStats && (
            <Stat
              label="Races won"
              value={`🏆 ${raceStats.wins}`}
              hint={`${raceStats.played} race${raceStats.played === 1 ? "" : "s"} played`}
            />
          )}
        </div>
      </section>

      <section className="mt-4 rounded-lg border border-line bg-surface p-5">
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-sm">
            <span className="font-semibold">{yearSubmissions}</span>{" "}
            <span className="text-muted">submission{yearSubmissions === 1 ? "" : "s"} in the past year</span>
          </h2>
          {isOwn && (
            <Link href="/submissions" className="text-sm text-accent hover:underline">
              All submissions →
            </Link>
          )}
        </div>
        <ActivityCalendar activity={activity} today={today} />
      </section>
    </main>
  );
}
