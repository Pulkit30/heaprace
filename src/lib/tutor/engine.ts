import "server-only";
import type { Problem } from "../problems";
import { explainError, getHint, getPatternForProblem, getProblemNotes, HINT_LEVELS, searchKnowledge, type KbHit } from "./tools";

// The HeapRace tutor agent. It runs without a paid LLM: a planner reads the learner's message,
// decides which tools to call (inspect the latest result, retrieve notes, reveal the next hint...),
// runs them, and composes a grounded reply that cites its sources. Every step is returned, so the UI
// can show how the answer was reached. It never produces solution code: the knowledge base has none.

export type TutorAction = "hint" | "debug" | "pattern" | "complexity";
export type TutorIntent = TutorAction | "solution-request" | "ask";

export interface TutorResultContext {
  verdict: "Accepted" | "Wrong Answer" | "Runtime Error" | "Time Limit Exceeded";
  /** "run" (sample tests in the browser) or "submit" (all tests on the server). */
  mode: "run" | "submit";
  error?: string;
  input?: string;
  actual?: string;
  expected?: string;
}

export interface TutorRequest {
  problem: Problem;
  message: string;
  action?: TutorAction;
  /** How many hints this learner has already seen for this problem (0–3). */
  hintsRevealed: number;
  lastResult?: TutorResultContext;
}

export interface TutorStep {
  tool: string;
  label: string;
}

export interface TutorBlock {
  title?: string;
  text: string;
  /** "code" renders monospaced (inputs and outputs, never solutions). */
  style?: "code" | "note";
}

export interface TutorReply {
  intent: TutorIntent;
  steps: TutorStep[];
  blocks: TutorBlock[];
  sources: string[];
  hintsRevealed: number;
  /** Buttons the UI can offer next. */
  suggestions: TutorAction[];
}

const has = (text: string, re: RegExp) => re.test(text.toLowerCase());

/** Decide what the learner wants. Buttons pass an explicit action; free text is classified. */
export function classify(message: string, action?: TutorAction): TutorIntent {
  if (action) return action;
  const m = message.trim();
  if (has(m, /\b(full|complete|whole|entire|final)\s+(solution|code|answer)\b|\bgive me the (code|solution)\b|\bwrite (the|my) (code|solution)\b|\bsolve it\b/)) {
    return "solution-request";
  }
  if (has(m, /\b(why|wrong|fail|failing|failed|error|exception|bug|crash|traceback|tle|slow|time limit|not working|doesn'?t work)\b/)) return "debug";
  if (has(m, /\b(complexity|big ?o|o\(|optimal|efficient|faster|runtime)\b/)) return "complexity";
  if (has(m, /\b(pattern|approach|technique|which algorithm|what algorithm|category|topic|strategy)\b/)) return "pattern";
  if (has(m, /\b(hint|stuck|start|where do i begin|clue|nudge|help me)\b/)) return "hint";
  return "ask";
}

export async function runTutor(req: TutorRequest): Promise<TutorReply> {
  const { problem } = req;
  const intent = classify(req.message, req.action);
  const steps: TutorStep[] = [];
  const blocks: TutorBlock[] = [];
  const sources = new Set<string>();
  let hintsRevealed = Math.max(0, Math.min(HINT_LEVELS, req.hintsRevealed));

  const cite = (hits: KbHit[]) => hits.forEach((h) => sources.add(h.title));

  async function revealHint() {
    if (hintsRevealed >= HINT_LEVELS) {
      const insight = await getProblemNotes(problem.slug, "insight");
      steps.push({ tool: "get_problem_notes", label: "All hints already shown, so I retrieved the key idea" });
      cite(insight);
      insight.forEach((h) => blocks.push({ title: "Key idea", text: h.body }));
      blocks.push({
        style: "note",
        text: "That's everything I can share without writing the code for you. Try turning the idea into steps in your editor, then use Run and ask me why it fails.",
      });
      return;
    }
    const hint = await getHint(problem.slug, hintsRevealed + 1);
    steps.push({ tool: "get_hint", label: `Revealed hint ${hintsRevealed + 1} of ${HINT_LEVELS}` });
    if (hint) {
      hintsRevealed++;
      cite([hint]);
      blocks.push({ title: `Hint ${hintsRevealed} of ${HINT_LEVELS}`, text: hint.body });
    }
  }

  switch (intent) {
    case "solution-request": {
      steps.push({ tool: "policy", label: "Solution requests get hints instead" });
      blocks.push({
        text: "I won't write the solution for you, because working it out is how the pattern sticks. I can take you there one step at a time, though:",
      });
      await revealHint();
      break;
    }

    case "hint":
      await revealHint();
      break;

    case "debug": {
      const r = req.lastResult;
      if (!r) {
        steps.push({ tool: "inspect_result", label: "Looked for your latest Run or Submit result: none yet" });
        blocks.push({
          text: "I don't have a result to look at yet. Press Run (it checks the sample tests), then ask me again and I'll explain what went wrong.",
        });
        break;
      }
      steps.push({ tool: "inspect_result", label: `Checked your latest ${r.mode === "submit" ? "submission" : "run"}: ${r.verdict}` });

      if (r.verdict === "Accepted") {
        blocks.push({
          text:
            r.mode === "run"
              ? "Your code passes the sample tests. Submit it to check the hidden tests too, and compare your approach with the target complexity:"
              : "Your submission passed every test. Nice work! Compare your approach with the target complexity:",
        });
        const cx = await getProblemNotes(problem.slug, "complexity");
        steps.push({ tool: "get_problem_notes", label: "Retrieved the target complexity" });
        cite(cx);
        cx.forEach((h) => blocks.push({ title: "Target", text: h.body }));
        break;
      }

      if (r.input) blocks.push({ title: "Failing input", text: r.input, style: "code" });
      if (r.verdict === "Wrong Answer" && r.actual !== undefined) {
        blocks.push({ title: "Your output vs expected", text: `yours:    ${r.actual}\nexpected: ${r.expected ?? "?"}`, style: "code" });
      }

      const errorText = r.verdict === "Runtime Error" ? (r.error ?? "") : r.verdict;
      const guides = await explainError(errorText || r.verdict);
      steps.push({ tool: "explain_error", label: `Matched the error against the error guides${guides[0] ? `: ${guides[0].title}` : ""}` });
      cite(guides);
      guides.forEach((g) => blocks.push({ title: g.title, text: g.body }));

      const line = r.error?.match(/line (\d+)/g)?.pop();
      if (line) blocks.push({ style: "note", text: `The traceback points at ${line} of your code. Start there.` });

      if (r.verdict === "Wrong Answer") {
        const pitfalls = await getProblemNotes(problem.slug, "pitfall");
        steps.push({ tool: "get_problem_notes", label: "Retrieved common mistakes for this problem" });
        cite(pitfalls);
        if (pitfalls.length) blocks.push({ title: "Common mistakes here", text: pitfalls.map((p) => `• ${p.body}`).join("\n") });
      }
      if (r.verdict === "Time Limit Exceeded") {
        const cx = await getProblemNotes(problem.slug, "complexity");
        steps.push({ tool: "get_problem_notes", label: "Retrieved the target complexity" });
        cite(cx);
        cx.forEach((h) => blocks.push({ title: "Target", text: h.body }));
      }
      break;
    }

    case "pattern": {
      const pattern = await getPatternForProblem(problem.slug);
      steps.push({ tool: "get_pattern", label: pattern ? `Looked up the roadmap: ${pattern.title}` : "Looked up the roadmap" });
      if (pattern) {
        cite([pattern]);
        blocks.push({ title: `Pattern: ${pattern.title}`, text: pattern.body });
        blocks.push({ style: "note", text: "See where it fits on the Roadmap page, together with the patterns to learn before and after it." });
      }
      break;
    }

    case "complexity": {
      const cx = await getProblemNotes(problem.slug, "complexity");
      steps.push({ tool: "get_problem_notes", label: "Retrieved the target complexity" });
      cite(cx);
      cx.forEach((h) => blocks.push({ title: "Target", text: h.body }));
      if (problem.constraints.length) {
        blocks.push({
          title: "Why",
          text: `The constraints (${problem.constraints.join("; ")}) decide what's fast enough: around 10⁸ simple steps per second in Python is optimistic, so n = 10⁵ rules out O(n²).`,
        });
      }
      break;
    }

    case "ask": {
      const hits = await searchKnowledge(`${req.message} ${problem.title}`, { slug: problem.slug, limit: 3 });
      steps.push({ tool: "search_knowledge", label: `Searched the knowledge base: ${hits.length} relevant note${hits.length === 1 ? "" : "s"}` });
      cite(hits);
      if (hits.length) {
        hits.forEach((h) => blocks.push({ title: h.title, text: h.body }));
      } else {
        blocks.push({
          text: "I couldn't find notes that match that question. Try asking for a hint, the pattern, the target complexity, or why your code is failing.",
        });
      }
      break;
    }
  }

  const suggestions: TutorAction[] = [];
  if (hintsRevealed < HINT_LEVELS && intent !== "hint") suggestions.push("hint");
  if (hintsRevealed < HINT_LEVELS && intent === "hint") suggestions.push("hint");
  if (intent !== "debug") suggestions.push("debug");
  if (intent !== "pattern") suggestions.push("pattern");
  if (intent !== "complexity") suggestions.push("complexity");

  return { intent, steps, blocks, sources: [...sources], hintsRevealed, suggestions: [...new Set(suggestions)].slice(0, 3) };
}
