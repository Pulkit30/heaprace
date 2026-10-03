import type { Metadata } from "next";
import Link from "next/link";
import ProblemTable from "@/components/ProblemTable";
import MonthCalendar from "@/components/progress/MonthCalendar";
import { getCurrentUser } from "@/lib/auth/server";
import { problems as basics } from "@/lib/problems";
import { getActivity, getUserStatuses, listProblems } from "@/lib/queries";
import { patterns } from "@/lib/roadmap";
import { computeStreaks, todayIn } from "@/lib/streak";
import { getUserTimeZone } from "@/lib/timezone";

export const metadata: Metadata = { title: "Problems" };

// The original hand-written set: a short starter list covering the core patterns.
const basicSlugs = new Set(basics.map((p) => p.slug));

const lists = [
  { id: "all", label: "All problems", href: "/problems" },
  { id: "basics", label: "Basics", href: "/problems?list=basics" },
] as const;

export default async function ProblemsPage({ searchParams }: PageProps<"/problems">) {
  const list = (await searchParams).list === "basics" ? "basics" : "all";
  const user = await getCurrentUser();
  const timeZone = await getUserTimeZone();
  const today = todayIn(timeZone);
  const [allProblems, statuses, activity] = await Promise.all([
    listProblems(),
    user ? getUserStatuses(user.id) : Promise.resolve({}),
    user ? getActivity(user.id, timeZone) : Promise.resolve([]),
  ]);
  const problems = list === "basics" ? allProblems.filter((p) => basicSlugs.has(p.slug)) : allProblems;
  const tags = Array.from(new Set(problems.flatMap((p) => p.tags))).sort();
  const shownPatterns = new Set(problems.map((p) => p.pattern));

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

        <nav aria-label="Problem lists" className="mt-6 flex gap-1 border-b border-line">
          {lists.map((l) => {
            const active = l.id === list;
            const count = l.id === "basics" ? basicSlugs.size : allProblems.length;
            return (
              <Link
                key={l.id}
                href={l.href}
                aria-current={active ? "page" : undefined}
                className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                  active ? "border-accent-fill text-fg" : "border-transparent text-muted hover:text-fg"
                }`}
              >
                {l.label} <span className="ml-1 text-xs text-muted">{count}</span>
              </Link>
            );
          })}
        </nav>
        {list === "basics" && (
          <p className="mt-3 text-sm text-muted">
            {basicSlugs.size} classic problems, one or two per core pattern. A good place to start before the full list.
          </p>
        )}

        <ProblemTable
          key={list}
          problems={problems}
          tags={tags}
          patterns={patterns.filter((p) => shownPatterns.has(p.id)).map(({ id, name }) => ({ id, name }))}
          statuses={statuses}
          showProgress={!!user}
        />
      </div>

      <aside className="lg:pt-[4.75rem]">
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
              className="mt-4 inline-block rounded-md bg-accent-fill px-4 py-1.5 text-sm font-medium text-on-accent transition-colors hover:bg-accent-strong"
            >
              Sign in
            </Link>
          </div>
        )}
      </aside>
    </main>
  );
}
