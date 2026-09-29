// Copies the Pyodide runtime from node_modules into public/pyodide so the app serves Python itself
// (no third-party CDN at runtime), and writes public/judge-harness.py from src/lib/judge/harness.ts.
// Runs automatically before `npm run dev` and `npm run build`.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { HARNESS_PY } from "../src/lib/judge/harness.ts";

const from = fileURLToPath(new URL("../node_modules/pyodide/", import.meta.url));
const to = fileURLToPath(new URL("../public/pyodide/", import.meta.url));
const files = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"];

mkdirSync(to, { recursive: true });
for (const f of files) {
  const src = from + f;
  const dest = to + f;
  if (existsSync(dest) && statSync(dest).size === statSync(src).size) continue;
  copyFileSync(src, dest);
  console.log(`copied pyodide/${f}`);
}

const harnessPath = fileURLToPath(new URL("../public/judge-harness.py", import.meta.url));
if (!existsSync(harnessPath) || readFileSync(harnessPath, "utf8") !== HARNESS_PY) {
  writeFileSync(harnessPath, HARNESS_PY);
  console.log("wrote judge-harness.py");
}
