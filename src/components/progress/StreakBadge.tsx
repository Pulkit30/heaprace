import Link from "next/link";

/** Navbar flame: orange once you've solved something today, grey while today's streak is still at risk. */
export default function StreakBadge({ current, solvedToday }: { current: number; solvedToday: boolean }) {
  const title = solvedToday
    ? `${current}-day streak. You've solved a problem today.`
    : current > 0
      ? `${current}-day streak. Solve a problem today to keep it going.`
      : "Solve a problem today to start a streak.";

  return (
    <Link
      href="/progress"
      title={title}
      aria-label={title}
      className={`flex items-center gap-1 rounded-md px-2 py-1 text-sm font-medium transition-colors hover:bg-surface-2 ${
        solvedToday ? "text-accent" : "text-muted"
      }`}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" className={solvedToday ? "" : "opacity-60"}>
        <path
          fill="currentColor"
          d="M12 2c.6 3.2-1 5.3-2.6 7.2C7.8 11 6 13 6 15.8 6 19.2 8.7 22 12 22s6-2.8 6-6.2c0-2.3-1.1-4.2-2.4-5.6-.2 1.5-1 2.7-2.1 3.1.4-2.9-.2-6.4-1.5-11.3z"
        />
      </svg>
      {current}
    </Link>
  );
}
