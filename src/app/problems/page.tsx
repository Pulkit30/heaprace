import type { Metadata } from "next";
import Link from "next/link";
import ProblemTable from "@/components/ProblemTable";
import { getCurrentUser } from "@/lib/auth/server";
import { getUserStatuses, listProblems } from "@/lib/queries";

export const metadata: Metadata = { title: "Problems" };

export default async function ProblemsPage() {
  const user = await getCurrentUser();
  const [problems, statuses] = await Promise.all([
    listProblems(),
    user ? getUserStatuses(user.id) : Promise.resolve({}),
  ]);
  const tags = Array.from(new Set(problems.flatMap((p) => p.tags))).sort();

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
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
    </main>
  );
}
