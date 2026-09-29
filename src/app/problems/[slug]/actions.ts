"use server";

import { refresh } from "next/cache";
import { getCurrentUser } from "@/lib/auth/server";
import { getProblem } from "@/lib/queries";
import { judgeAndRecord, type SubmitResult } from "@/lib/submit";

export interface SubmitInput {
  slug: string;
  code: string;
}

/** Practice submit: judged on the server against every test, including hidden ones, then saved. */
export async function submitSolution(input: SubmitInput): Promise<SubmitResult> {
  const user = await getCurrentUser();
  if (!user) return { ok: false, reason: "signed-out", message: "Sign in to submit." };
  if (typeof input?.slug !== "string") return { ok: false, reason: "invalid", message: "That submission isn't valid." };

  const problem = await getProblem(input.slug);
  if (!problem) return { ok: false, reason: "invalid", message: "Problem not found." };

  const res = await judgeAndRecord({ userId: user.id, problem, code: input.code });
  // Re-render server parts of the page (the navbar streak) without touching the editor's state.
  if (res.ok) refresh();
  return res;
}
