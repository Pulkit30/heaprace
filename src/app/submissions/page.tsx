import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import TimeAgo from "@/components/TimeAgo";
import VerdictText from "@/components/VerdictText";
import { getCurrentUser } from "@/lib/auth/server";
import { getRecentSubmissions, getUserStatuses } from "@/lib/queries";

export const metadata: Metadata = { title: "My submissions" };

export default async function SubmissionsPage() {
  // proxy.ts already redirects signed-out visitors; this check keeps the data safe on its own.
  const user = await getCurrentUser();
  if (!user) redirect("/auth/sign-in?next=/submissions");

  const [rows, statuses] = await Promise.all([getRecentSubmissions(user.id), getUserStatuses(user.id)]);
  const solved = Object.values(statuses).filter((s) => s === "solved").length;

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">My submissions</h1>
      <p className="mt-1 text-sm text-muted">
        {solved} solved · {Object.keys(statuses).length} attempted · {rows.length} recent submissions
      </p>

      {rows.length === 0 ? (
        <p className="mt-8 text-sm text-muted">
          Nothing yet.{" "}
          <Link href="/problems" className="text-accent hover:underline">
            Pick a problem
          </Link>{" "}
          and press Submit.
        </p>
      ) : (
        <div className="mt-6 overflow-x-auto rounded-lg border border-line">
          <table className="w-full min-w-[36rem] text-left text-sm">
            <thead className="bg-surface text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">When</th>
                <th className="px-4 py-3 font-medium">Problem</th>
                <th className="px-4 py-3 font-medium">Verdict</th>
                <th className="px-4 py-3 text-right font-medium">Tests</th>
                <th className="px-4 py-3 text-right font-medium">Runtime</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => (
                <tr key={s.id} className="border-t border-line">
                  <td className="whitespace-nowrap px-4 py-3 text-muted">
                    <TimeAgo iso={s.createdAt} />
                  </td>
                  <td className="px-4 py-3">
                    <Link href={`/problems/${s.problemSlug}`} className="hover:text-accent">
                      {s.problemTitle}
                    </Link>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3">
                    <VerdictText verdict={s.verdict} className="font-medium" />
                  </td>
                  <td className="px-4 py-3 text-right text-muted">
                    {s.passed}/{s.total}
                  </td>
                  <td className="px-4 py-3 text-right text-muted">{s.runtimeMs} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
