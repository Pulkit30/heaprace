import type { Metadata } from "next";
import Link from "next/link";
import ProblemTable from "@/components/ProblemTable";
import MonthCalendar from "@/components/progress/MonthCalendar";
import { getCurrentUser } from "@/lib/auth/server";
import { getActivity, getUserStatuses, listProblems } from "@/lib/queries";
import { computeStreaks, todayIn } from "@/lib/streak";
import { getUserTimeZone } from "@/lib/timezone";

export const metadata: Metadata = { title: "Problems" };

export default async function ProblemsPage() {
  const user = await getCurrentUser();
  const timeZone = await getUserTimeZone();
  const today = todayIn(timeZone);
  const [problems, statuses, activity] = await Promise.all([
    listProblems(),
    user ? getUserStatuses(user.id) : Promise.resolve({}),
    user ? getActivity(user.id, timeZone) : Promise.resolve([]),
  ]);
  const tags = Array.from(new Set(problems.flatMap((p) => p.tags))).sort();

  return (
    <main className="mx-auto grid w-full max-w-7xl flex-1 gap-6 px-4 py-10 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">Problems</h1>
        <p className="mt-1 text-sm text-muted">
          {user ? (
            "Pick one and start climbing."
          ) : (
            <>
              <Link href="/auth/sign-in" className="text-accent hover:underline">
                Sign in
              </Link>{" "}
              to save submissions and track what you&apos;ve solved.
            </>
          )}
        </p>
        <ProblemTable problems={problems} tags={tags} statuses={statuses} showProgress={!!user} />
      </div>

      <aside className="lg:pt-[3.75rem]">
        {user ? (
          <MonthCalendar activity={activity} today={today} streak={computeStreaks(activity, today)} />
        ) : (
          <div className="rounded-lg border border-line bg-surface p-5 text-center">
            <p className="text-2xl" aria-hidden="true">
              🔥
            </p>
            <p className="mt-2 text-sm font-medium">Build a daily streak</p>
            <p className="mt-1 text-xs text-muted">Solve a problem every day and watch your calendar fill up.</p>
            <Link
              href="/auth/sign-in"
              className="mt-4 inline-block rounded-md bg-accent-fill px-4 py-1.5 text-sm font-medium text-black transition-colors hover:bg-accent-strong"
            >
              Sign in
            </Link>
          </div>
        )}
      </aside>
    </main>
  );
}
