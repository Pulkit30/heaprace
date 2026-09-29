import Link from "next/link";
import type { RaceParticipantView } from "@/lib/race";
import { formatClock } from "./useRace";

const medal = ["🥇", "🥈", "🥉"];

export default function Leaderboard({
  participants,
  youId,
  running,
}: {
  participants: RaceParticipantView[];
  youId: string;
  running: boolean;
}) {
  return (
    <ol className="divide-y divide-line">
      {participants.map((p) => (
        <li
          key={p.userId}
          className={`flex items-center gap-3 px-4 py-3 text-sm ${p.userId === youId ? "bg-accent-fill/10" : ""}`}
        >
          <span className="w-6 text-center">
            {p.rank ? (medal[p.rank - 1] ?? <span className="text-muted">{p.rank}</span>) : <span className="text-muted">·</span>}
          </span>
          <span className="min-w-0 flex-1">
            <Link href={`/u/${p.userId}`} className="block truncate font-medium hover:text-accent">
              {p.name}
              {p.userId === youId && <span className="ml-1 text-xs font-normal text-muted">(you)</span>}
              {p.isHost && <span className="ml-1 text-xs font-normal text-muted">· host</span>}
            </Link>
            <span className="text-xs text-muted">
              {p.attempts} attempt{p.attempts === 1 ? "" : "s"}
            </span>
          </span>
          <span className={`text-right text-xs ${p.solveMs !== null ? "font-medium text-easy" : "text-muted"}`}>
            {p.solveMs !== null ? `✓ ${formatClock(p.solveMs)}` : running ? "solving…" : "didn't finish"}
          </span>
        </li>
      ))}
    </ol>
  );
}
