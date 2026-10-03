// Loads every problem: the hand-written ones in src/lib/problems.ts plus the catalog built from content/catalog/
// by content/build_catalog.py (which computes and cross-checks every expected output).
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { problems as handWritten, type Problem } from "../src/lib/problems.ts";
import { problemGuides, type ProblemGuide } from "../src/lib/tutor/knowledge.ts";

export interface FullProblem extends Problem {
  guide: Omit<ProblemGuide, "slug">;
}

const builder = fileURLToPath(new URL("../content/build_catalog.py", import.meta.url));
// Extra hidden tests (edge cases, generated and large inputs) for the hand-written problems.
const basicsBuilder = fileURLToPath(new URL("../content/build_basics.py", import.meta.url));

export function loadAllProblems(): FullProblem[] {
  const json = execFileSync("python3", [builder, "--existing-slugs", handWritten.map((p) => p.slug).join(",")], {
    encoding: "utf8",
    maxBuffer: 512 * 1024 * 1024,
    stdio: ["ignore", "pipe", "inherit"],
  });
  const catalog = JSON.parse(json) as FullProblem[];
  const extraTests = JSON.parse(
    execFileSync("python3", [basicsBuilder], {
      input: JSON.stringify(
        handWritten.map(({ slug, functionName, argTypes, returnType, compare, tests }) => ({ slug, functionName, argTypes, returnType, compare, tests })),
      ),
      encoding: "utf8",
      maxBuffer: 512 * 1024 * 1024,
      stdio: ["pipe", "pipe", "inherit"],
    }),
  ) as Record<string, Problem["tests"]>;
  const guides = new Map(problemGuides.map(({ slug, ...g }) => [slug, g]));
  const own = handWritten.map((p) => {
    const guide = guides.get(p.slug);
    if (!guide) throw new Error(`${p.slug}: no tutor guide in knowledge.ts`);
    return { ...p, tests: [...p.tests, ...(extraTests[p.slug] ?? [])], guide };
  });
  return [...own, ...catalog];
}
