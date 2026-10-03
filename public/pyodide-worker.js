// Module worker. Runs user Python in a Web Worker so an infinite loop can be killed (worker.terminate) without freezing the page.
// Protocol:  in  { type: "run", id, code, functionName, args, argTypes?, returnType?, options? }
//            out { type: "ready" } | { type: "init-error", error } | { type: "result", id, ok, result?, error?, stdout, timeMs }

// Pyodide is self-hosted from /pyodide (copied from node_modules by scripts/copy-pyodide.ts).
import { loadPyodide } from "/pyodide/pyodide.mjs";

// The harness Python is generated from src/lib/judge/harness.ts (shared with the server judge).
const harnessSource = fetch("/judge-harness.py").then((r) => {
  if (!r.ok) throw new Error(`judge-harness.py: HTTP ${r.status}`);
  return r.text();
});

const ready = (async () => {
  const [pyodide, harness] = await Promise.all([loadPyodide({ indexURL: "/pyodide/" }), harnessSource]);
  pyodide.runPython(harness);
  return pyodide;
})();

ready.then(
  () => postMessage({ type: "ready" }),
  (err) => postMessage({ type: "init-error", error: String(err) }),
);

onmessage = async ({ data }) => {
  if (data.type !== "run") return;
  const pyodide = await ready;
  const run = pyodide.globals.get("__heaprace_run");
  const start = performance.now();
  try {
    const raw = run(
      data.code,
      data.functionName,
      JSON.stringify(data.args),
      JSON.stringify(data.argTypes ?? null),
      data.returnType ?? null,
      JSON.stringify(data.options ?? null),
    );
    postMessage({ type: "result", id: data.id, timeMs: performance.now() - start, ...JSON.parse(raw) });
  } catch (err) {
    postMessage({ type: "result", id: data.id, ok: false, error: String(err), stdout: "", timeMs: performance.now() - start });
  } finally {
    run.destroy();
  }
};
