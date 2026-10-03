"use server";

import { getProblem } from "@/lib/queries";
import { runTutor, type TutorAction, type TutorReply, type TutorResultContext } from "@/lib/tutor/engine";

const ACTIONS: TutorAction[] = ["hint", "debug", "pattern", "complexity"];
const VERDICTS: TutorResultContext["verdict"][] = ["Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded"];

export interface AskTutorInput {
  slug: string;
  message: string;
  action?: TutorAction;
  hintsRevealed: number;
  lastResult?: TutorResultContext;
}

const clip = (v: unknown, n: number) => (typeof v === "string" ? v.slice(0, n) : undefined);

/** Ask the tutor about a problem. Free and open to everyone; it only ever returns hints and explanations. */
export async function askTutor(input: AskTutorInput): Promise<TutorReply | { error: string }> {
  if (typeof input?.slug !== "string") return { error: "Unknown problem." };
  const problem = await getProblem(input.slug);
  if (!problem) return { error: "Unknown problem." };

  const r = input.lastResult;
  const lastResult: TutorResultContext | undefined =
    r && VERDICTS.includes(r.verdict)
      ? {
          verdict: r.verdict,
          mode: r.mode === "submit" ? "submit" : "run",
          error: clip(r.error, 2000),
          input: clip(r.input, 600),
          actual: clip(r.actual, 600),
          expected: clip(r.expected, 600),
        }
      : undefined;

  return runTutor({
    // Only the public parts matter to the tutor; hidden tests are never sent back.
    problem: { ...problem, tests: [] },
    message: clip(input.message, 500) ?? "",
    action: ACTIONS.includes(input.action as TutorAction) ? input.action : undefined,
    hintsRevealed: Number.isInteger(input.hintsRevealed) ? input.hintsRevealed : 0,
    lastResult,
  });
}
