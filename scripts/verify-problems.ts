// Checks every test case in src/lib/problems.ts against scripts/reference_solutions.py.
// Run with: npm run verify:problems
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { problems } from "../src/lib/problems.ts";
import { isCorrect, formatValue } from "../src/lib/judge/compare.ts";

const refScript = fileURLToPath(new URL("./reference_solutions.py", import.meta.url));
const input = JSON.stringify(problems.map(({ slug, functionName, tests }) => ({ slug, functionName, tests })));
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

if (failures) {
  console.log(`\n${failures} problem(s) found`);
  process.exit(1);
}
console.log(`\nAll ${problems.length} problems verified.`);
