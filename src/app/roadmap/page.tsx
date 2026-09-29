import type { Metadata } from "next";
import Link from "next/link";
import RoadmapView from "@/components/roadmap/RoadmapView";
import { getCurrentUser } from "@/lib/auth/server";
import { getUserStatuses, listProblems } from "@/lib/queries";
import { patterns } from "@/lib/roadmap";

export const metadata: Metadata = { title: "Roadmap" };

export default async function RoadmapPage() {
  const user = await getCurrentUser();
  const [problems, statuses] = await Promise.all([
    listProblems(),
    user ? getUserStatuses(user.id) : Promise.resolve({}),
  ]);
  const solved = Object.values(statuses).filter((s) => s === "solved").length;

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Roadmap</h1>
          <p className="mt-1 text-sm text-muted">
            {patterns.length} patterns, from the basics down to graphs and dynamic programming. Click a pattern to see its
            problems.
          </p>
        </div>
        <p className="text-sm text-muted">
          {user ? (
            <>
              <span className="font-medium text-fg">{solved}</span>/{problems.length} problems solved
            </>
          ) : (
            <>
              <Link href="/auth/sign-in?next=/roadmap" className="text-accent hover:underline">
                Sign in
              </Link>{" "}
              to track your progress
            </>
          )}
        </p>
      </div>
      <RoadmapView problems={problems} statuses={statuses} signedIn={!!user} />
    </main>
  );
}
