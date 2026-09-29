import type { Metadata } from "next";
import Link from "next/link";
import TimeAgo from "@/components/TimeAgo";
import { CreateRaceForm, JoinRaceForm } from "@/components/race/RaceForms";
import { getCurrentUser } from "@/lib/auth/server";
import { DURATIONS_MIN, getRecentRaces, MAX_PARTICIPANTS } from "@/lib/race";

export const metadata: Metadata = { title: "Race" };

const phaseLabel = { lobby: "In lobby", countdown: "Starting", running: "Live", finished: "Finished" } as const;

export default async function RaceHome() {
  const user = await getCurrentUser();
  const recent = user ? await getRecentRaces(user.id) : [];

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <p className="text-sm font-medium uppercase tracking-widest text-accent">Race mode</p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight">Same problem. Same clock. First to Accepted wins.</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Create a room, share the code with up to {MAX_PARTICIPANTS - 1} friends, and start when everyone is in. A random
        problem is revealed after a 5-second countdown, and every submission is judged on the server.
      </p>

      {!user ? (
        <div className="mt-8 rounded-xl border border-line bg-surface p-6">
          <p className="font-medium">Sign in to race</p>
          <p className="mt-1 text-sm text-muted">Races need an account so standings and wins are saved.</p>
          <Link
            href="/auth/sign-in?next=/race"
            className="mt-4 inline-block rounded-md bg-accent-fill px-4 py-2 text-sm font-medium text-black hover:bg-accent-strong"
          >
            Sign in
          </Link>
        </div>
      ) : (
        <>
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <section className="rounded-xl border border-line bg-surface p-6">
              <h2 className="mb-4 font-semibold">Create a race</h2>
              <CreateRaceForm durations={DURATIONS_MIN} />
            </section>
            <section className="rounded-xl border border-line bg-surface p-6">
              <h2 className="mb-4 font-semibold">Join with a code</h2>
              <JoinRaceForm />
            </section>
          </div>

          {recent.length > 0 && (
            <section className="mt-8">
              <h2 className="mb-3 font-semibold">Your recent races</h2>
              <ul className="divide-y divide-line overflow-hidden rounded-lg border border-line bg-surface">
                {recent.map((r) => (
                  <li key={r.code}>
                    <Link href={`/race/${r.code}`} className="flex items-center gap-4 px-4 py-3 text-sm hover:bg-surface-2">
                      <span className="font-mono font-medium tracking-widest">{r.code}</span>
                      <span className={r.phase === "running" ? "font-medium text-easy" : "text-muted"}>{phaseLabel[r.phase]}</span>
                      <span className="text-muted">
                        {r.players} player{r.players === 1 ? "" : "s"}
                      </span>
                      <span className="ml-auto text-muted">
                        {r.rank ? (r.rank === 1 ? "🏆 Won" : `#${r.rank}`) : r.phase === "finished" ? "Didn't finish" : ""}
                      </span>
                      <span className="hidden w-28 text-right text-muted sm:inline">
                        <TimeAgo iso={r.createdAt} />
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </main>
  );
}
