"use client";

import Link from "next/link";
import { useActionState, useState, useTransition } from "react";
import { cancelRace, joinRace, leaveRace, startRace, submitRaceSolution } from "@/app/race/actions";
import type { RaceState } from "@/lib/race";
import DifficultyBadge from "../DifficultyBadge";
import Workspace from "../workspace/Workspace";
import Leaderboard from "./Leaderboard";
import { formatClock, useRace, useServerNow } from "./useRace";

const card = "rounded-xl border border-line bg-surface";
const primaryButton =
  "rounded-md bg-accent-fill px-5 py-2 text-sm font-medium text-black transition-colors hover:bg-accent-strong disabled:opacity-50";
const secondaryButton =
  "rounded-md border border-line px-4 py-2 text-sm text-muted transition-colors hover:bg-surface-2 hover:text-fg";

export default function RaceRoom({ initial }: { initial: RaceState }) {
  const { state, offsetMs, refresh, lost } = useRace(initial);

  if (lost) {
    return (
      <Centered>
        <p className="text-lg font-semibold">This race no longer exists</p>
        <p className="mt-1 text-sm text-muted">The host may have cancelled it.</p>
        <Link href="/race" className={`${primaryButton} mt-6 inline-block`}>
          Back to races
        </Link>
      </Centered>
    );
  }

  const startsAt = state.startsAt ? Date.parse(state.startsAt) : null;
  const endsAt = state.endsAt ? Date.parse(state.endsAt) : null;

  if (state.phase === "lobby") return <Lobby state={state} onChange={refresh} />;

  // The server says countdown, or we've just passed the start and are waiting for the next poll.
  if (state.phase === "countdown" || (state.phase === "running" && !state.problem && state.isParticipant)) {
    return (
      <Centered>
        <p className="text-sm uppercase tracking-widest text-muted">Race {state.code}</p>
        <Countdown startsAt={startsAt ?? 0} offsetMs={offsetMs} />
      </Centered>
    );
  }

  if (state.phase === "running" && state.problem) {
    const me = state.participants.find((p) => p.userId === state.youId);
    return (
      <div className="flex flex-1 flex-col">
        <div className="flex h-10 shrink-0 items-center gap-4 border-b border-line bg-surface px-4 text-sm">
          <span className="font-medium">Race {state.code}</span>
          <TimeLeft endsAt={endsAt ?? 0} offsetMs={offsetMs} />
          <span className="hidden text-muted sm:inline">
            {state.participants.filter((p) => p.rank).length}/{state.participants.length} finished
          </span>
          {me?.rank && (
            <span className="ml-auto font-medium text-easy">
              You finished #{me.rank} in {formatClock(me.solveMs ?? 0)}
            </span>
          )}
        </div>
        <Workspace
          problem={state.problem}
          signedIn
          initialSubmissions={[]}
          draftKey={`race:${state.code}`}
          heightClass="lg:h-[calc(100dvh-6rem)]"
          submit={async (code) => {
            const res = await submitRaceSolution(state.code, code);
            void refresh();
            return res;
          }}
          extraTab={{
            label: "Standings",
            content: <Leaderboard participants={state.participants} youId={state.youId} running />,
          }}
        />
      </div>
    );
  }

  if (state.phase === "running") {
    // Someone who didn't join before the start: watch the standings.
    return (
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-10">
        <h1 className="text-2xl font-semibold tracking-tight">Race {state.code} is in progress</h1>
        <p className="mt-1 text-sm text-muted">
          <TimeLeft endsAt={endsAt ?? 0} offsetMs={offsetMs} /> · You can watch the standings live.
        </p>
        <div className={`${card} mt-6 overflow-hidden`}>
          <Leaderboard participants={state.participants} youId={state.youId} running />
        </div>
      </main>
    );
  }

  return <Results state={state} />;
}

// The timers own the 4×-a-second clock, so only they re-render, never the code editor.
function Countdown({ startsAt, offsetMs }: { startsAt: number; offsetMs: number }) {
  const left = startsAt - useServerNow(offsetMs);
  return left > 0 ? (
    <>
      <p className="mt-6 text-8xl font-bold tabular-nums text-accent">{Math.ceil(left / 1000)}</p>
      <p className="mt-4 text-sm text-muted">Get ready. The problem appears when the countdown ends.</p>
    </>
  ) : (
    <p className="mt-6 text-lg text-muted">Loading the problem…</p>
  );
}

function TimeLeft({ endsAt, offsetMs }: { endsAt: number; offsetMs: number }) {
  const left = endsAt - useServerNow(offsetMs);
  return (
    <span className={`tabular-nums ${left < 60_000 ? "font-semibold text-hard" : "text-muted"}`}>
      ⏱ {left > 0 ? `${formatClock(left)} left` : "Time's up"}
    </span>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <main className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">{children}</main>;
}

function Lobby({ state, onChange }: { state: RaceState; onChange: () => Promise<void> }) {
  const [copied, setCopied] = useState(false);
  const [starting, startTransition] = useTransition();
  const [startError, setStartError] = useState<string | null>(null);
  const [joinState, joinAction, joining] = useActionState(joinRace, null);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/race/${state.code}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard blocked: the code is on screen anyway.
    }
  }

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
      <div className={`${card} p-6 sm:p-8`}>
        <p className="text-xs uppercase tracking-widest text-muted">Race room</p>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h1 className="font-mono text-4xl font-bold tracking-[0.2em]">{state.code}</h1>
          <button onClick={copyLink} className={secondaryButton}>
            {copied ? "Link copied ✓" : "Copy invite link"}
          </button>
        </div>
        <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
          <span>
            Difficulty: {state.difficulty ? <DifficultyBadge difficulty={state.difficulty} /> : <span className="text-fg">Any</span>}
          </span>
          <span>·</span>
          <span>
            Length: <span className="text-fg">{state.durationSec / 60} minutes</span>
          </span>
          <span>·</span>
          <span>The problem stays secret until the race starts.</span>
        </p>

        <h2 className="mt-8 mb-3 text-sm font-semibold">
          Players <span className="font-normal text-muted">({state.participants.length}/{state.maxParticipants})</span>
        </h2>
        <ul className="flex flex-wrap gap-2">
          {state.participants.map((p) => (
            <li
              key={p.userId}
              className={`rounded-full border px-3 py-1 text-sm ${p.userId === state.youId ? "border-accent-fill" : "border-line"}`}
            >
              {p.name}
              {p.isHost && <span className="ml-1 text-xs text-muted">host</span>}
            </li>
          ))}
        </ul>

        <div className="mt-8 flex flex-wrap items-center gap-3">
          {state.isHost ? (
            <>
              <button
                disabled={starting}
                onClick={() =>
                  startTransition(async () => {
                    const res = await startRace(state.code);
                    setStartError(res.error ?? null);
                    await onChange();
                  })
                }
                className={primaryButton}
              >
                {starting ? "Starting…" : state.participants.length > 1 ? "Start race" : "Start solo race"}
              </button>
              <form action={cancelRace.bind(null, state.code)}>
                <button className={secondaryButton}>Cancel room</button>
              </form>
              <span className="text-xs text-muted">Share the code or link, then start when everyone is in.</span>
            </>
          ) : state.isParticipant ? (
            <>
              <span className="flex items-center gap-2 text-sm text-muted">
                <span className="h-2 w-2 animate-pulse rounded-full bg-medium" aria-hidden="true" />
                Waiting for the host to start…
              </span>
              <form action={leaveRace.bind(null, state.code)}>
                <button className={secondaryButton}>Leave</button>
              </form>
            </>
          ) : (
            <form action={joinAction}>
              <input type="hidden" name="code" value={state.code} />
              <button disabled={joining || state.participants.length >= state.maxParticipants} className={primaryButton}>
                {joining ? "Joining…" : "Join race"}
              </button>
            </form>
          )}
        </div>
        {(startError || joinState?.error) && <p className="mt-3 text-sm text-hard">{startError ?? joinState?.error}</p>}
      </div>
    </main>
  );
}

function Results({ state }: { state: RaceState }) {
  const winner = state.participants.find((p) => p.rank === 1);
  const me = state.participants.find((p) => p.userId === state.youId);
  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
      <div className={`${card} p-6 text-center sm:p-8`}>
        <p className="text-xs uppercase tracking-widest text-muted">Race {state.code} · finished</p>
        {winner ? (
          <>
            <p className="mt-4 text-5xl" aria-hidden="true">
              🏆
            </p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight">
              {winner.userId === state.youId ? "You won!" : `${winner.name} won`}
            </h1>
            <p className="mt-1 text-sm text-muted">Solved in {formatClock(winner.solveMs ?? 0)}</p>
          </>
        ) : (
          <h1 className="mt-4 text-2xl font-semibold tracking-tight">Time&apos;s up. Nobody solved it this time.</h1>
        )}
        {me && me.rank && me.rank > 1 && <p className="mt-2 text-sm">You finished #{me.rank}.</p>}
        {state.revealedProblem && (
          <p className="mt-4 text-sm text-muted">
            The problem was{" "}
            <Link href={`/problems/${state.revealedProblem.slug}`} className="font-medium text-accent hover:underline">
              {state.revealedProblem.title}
            </Link>{" "}
            (<DifficultyBadge difficulty={state.revealedProblem.difficulty} />
            ). Practice it any time.
          </p>
        )}
      </div>

      <div className={`${card} mt-4 overflow-hidden`}>
        <h2 className="border-b border-line px-4 py-3 text-sm font-semibold">Final standings</h2>
        <Leaderboard participants={state.participants} youId={state.youId} running={false} />
      </div>

      <div className="mt-6 flex justify-center gap-3">
        <Link href="/race" className={primaryButton}>
          New race
        </Link>
        <Link href="/problems" className={secondaryButton}>
          Practice problems
        </Link>
      </div>
    </main>
  );
}
