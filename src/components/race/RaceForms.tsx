"use client";

import { useActionState } from "react";
import { createRace, joinRace } from "@/app/race/actions";

const field =
  "w-full rounded-md border border-line bg-surface-2 px-3 py-2 text-sm outline-none focus:border-accent-fill";
const primaryButton =
  "w-full rounded-md bg-accent-fill px-4 py-2 text-sm font-medium text-on-accent transition-colors hover:bg-accent-strong disabled:opacity-50";

export function CreateRaceForm({ durations }: { durations: readonly number[] }) {
  const [state, action, pending] = useActionState(createRace, null);
  return (
    <form action={action} className="space-y-4">
      <label className="block">
        <span className="mb-1.5 block text-sm">Difficulty</span>
        <select name="difficulty" defaultValue="any" className={field}>
          <option value="any">Any</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
      </label>
      <label className="block">
        <span className="mb-1.5 block text-sm">Length</span>
        <select name="duration" defaultValue="20" className={field}>
          {durations.map((m) => (
            <option key={m} value={m}>
              {m} minutes
            </option>
          ))}
        </select>
      </label>
      {state?.error && <p className="text-sm text-hard">{state.error}</p>}
      <button disabled={pending} className={primaryButton}>
        {pending ? "Creating…" : "Create race room"}
      </button>
    </form>
  );
}

export function JoinRaceForm() {
  const [state, action, pending] = useActionState(joinRace, null);
  return (
    <form action={action} className="space-y-4">
      <label className="block">
        <span className="mb-1.5 block text-sm">Room code</span>
        <input
          name="code"
          required
          maxLength={6}
          autoComplete="off"
          autoCapitalize="characters"
          spellCheck={false}
          placeholder="e.g. X7K2QP"
          className={`${field} font-mono uppercase tracking-[0.2em] placeholder:tracking-normal`}
        />
      </label>
      {state?.error && <p className="text-sm text-hard">{state.error}</p>}
      <button disabled={pending} className={primaryButton}>
        {pending ? "Joining…" : "Join race"}
      </button>
    </form>
  );
}
