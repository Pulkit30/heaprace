// Checks every test case in src/lib/problems.ts against scripts/reference_solutions.py,
// and that src/lib/roadmap.ts only references real problems and patterns.
// Run with: npm run verify:problems
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { problems } from "../src/lib/problems.ts";
import { isCorrect, formatValue } from "../src/lib/judge/compare.ts";
import { patterns } from "../src/lib/roadmap.ts";
import { errorGuides, patternNotes, problemGuides } from "../src/lib/tutor/knowledge.ts";

const refScript = fileURLToPath(new URL("./reference_solutions.py", import.meta.url));
const input = JSON.stringify(problems.map(({ slug, functionName, tests, argTypes, returnType }) => ({ slug, functionName, tests, argTypes, returnType })));
const results: Record<string, unknown[] | null> = JSON.parse(
  execFileSync("python3", [refScript], { input, encoding: "utf8" }),
);

let failures = 0;
const slugs = new Set<string>();

for (const p of problems) {
  const problemErrors: string[] = [];
  if (slugs.has(p.slug)) problemErrors.push("duplicate slug");
  slugs.add(p.slug);
  if (!p.tests.some((t) => t.sample)) problemErrors.push("no sample tests");
  if (!p.starterCode.includes(`def ${p.functionName}(`)) problemErrors.push("starter code is missing the method");

  const actual = results[p.slug];
  if (!actual) {
    problemErrors.push("no reference solution");
  } else {
    p.tests.forEach((t, i) => {
      if (!isCorrect(actual[i], t.expected, p.compare)) {
        problemErrors.push(`test ${i + 1}: expected ${formatValue(t.expected)}, reference gave ${formatValue(actual[i])}`);
      }
    });
  }

  if (problemErrors.length) {
    failures += problemErrors.length;
    console.log(`✗ ${p.slug}\n  ${problemErrors.join("\n  ")}`);
  } else {
    console.log(`✓ ${p.slug} (${p.tests.length} tests)`);
  }
}

const roadmapErrors: string[] = [];
const patternById = new Map(patterns.map((p) => [p.id, p]));
if (patterns.length !== 28) roadmapErrors.push(`expected 28 patterns, found ${patterns.length}`);
if (patternById.size !== patterns.length) roadmapErrors.push("duplicate pattern id");
const placed = new Set<string>();
for (const pat of patterns) {
  for (const parent of pat.parents) {
    const pp = patternById.get(parent);
    if (!pp) roadmapErrors.push(`${pat.id}: unknown parent "${parent}"`);
    else if (pp.row >= pat.row) roadmapErrors.push(`${pat.id}: parent "${parent}" must be on an earlier row`);
  }
  if (pat.problems.length === 0) roadmapErrors.push(`${pat.id}: has no problems`);
  for (const slug of pat.problems) {
    if (!slugs.has(slug)) roadmapErrors.push(`${pat.id}: unknown problem "${slug}"`);
    if (placed.has(slug)) roadmapErrors.push(`${pat.id}: "${slug}" is already in another pattern`);
    placed.add(slug);
  }
}
if (roadmapErrors.length) {
  failures += roadmapErrors.length;
  console.log(`✗ roadmap\n  ${roadmapErrors.join("\n  ")}`);
} else {
  console.log(`✓ roadmap (${patterns.length} patterns, ${placed.size}/${problems.length} problems placed)`);
}

const kbErrors: string[] = [];
const guideSlugs = new Set(problemGuides.map((g) => g.slug));
for (const p of problems) if (!guideSlugs.has(p.slug)) kbErrors.push(`${p.slug}: no tutor guide (hints) in knowledge.ts`);
for (const g of problemGuides) {
  if (!slugs.has(g.slug)) kbErrors.push(`${g.slug}: guide for an unknown problem`);
  if (g.hints.some((h) => h.trim().length < 20)) kbErrors.push(`${g.slug}: a hint is too short`);
  // The tutor must never hand out solutions: guides are prose only.
  if ([...g.hints, g.insight, ...g.pitfalls].some((t) => /\bdef |\breturn |class Solution|\n\s{4}/.test(t))) {
    kbErrors.push(`${g.slug}: guide text looks like code`);
  }
}
for (const pat of patterns) if (!patternNotes.some((n) => n.patternId === pat.id)) kbErrors.push(`${pat.id}: no pattern note`);
if (new Set(errorGuides.map((e) => e.id)).size !== errorGuides.length) kbErrors.push("duplicate error guide id");
if (kbErrors.length) {
  failures += kbErrors.length;
  console.log(`✗ tutor knowledge\n  ${kbErrors.join("\n  ")}`);
} else {
  console.log(`✓ tutor knowledge (${problemGuides.length} problem guides, ${patternNotes.length} pattern notes, ${errorGuides.length} error guides)`);
}

if (failures) {
  console.log(`\n${failures} problem(s) found`);
  process.exit(1);
}
console.log(`\nAll ${problems.length} problems verified.`);
