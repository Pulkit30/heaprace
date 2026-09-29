// Module worker. Runs user Python in a Web Worker so an infinite loop can be killed (worker.terminate) without freezing the page.
// Protocol:  in  { type: "run", id, code, functionName, args }
//            out { type: "ready" } | { type: "init-error", error } | { type: "result", id, ok, result?, error?, stdout, timeMs }

// Pyodide is self-hosted from /pyodide (copied from node_modules by scripts/copy-pyodide.ts).
import { loadPyodide } from "/pyodide/pyodide.mjs";

const HARNESS = `
import io, json, linecache, sys, traceback

MAX_STDOUT = 10_000

def _to_json(v):
    if isinstance(v, (set, frozenset, tuple)):
        return list(v)
    raise TypeError(f"Return value of type {type(v).__name__} can't be judged")

def __heaprace_run(code, fn_name, args_json):
    out = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = out
    try:
        # Register the source so tracebacks can show the failing line.
        linecache.cache["solution.py"] = (len(code), None, code.splitlines(True), "solution.py")
        ns = {"__name__": "solution"}
        exec(compile(code, "solution.py", "exec"), ns)
        if "Solution" in ns:
            if not hasattr(ns["Solution"], fn_name):
                raise AttributeError(f"class Solution has no method '{fn_name}'")
            fn = getattr(ns["Solution"](), fn_name)
        elif fn_name in ns:
            fn = ns[fn_name]
        else:
            raise NameError(f"Define class Solution with a method named '{fn_name}'")
        result = fn(*json.loads(args_json))
        return json.dumps({"ok": True, "result": json.loads(json.dumps(result, default=_to_json)), "stdout": out.getvalue()[:MAX_STDOUT]})
    except BaseException as e:
        frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == "solution.py"]
        lines = ["Traceback (most recent call last):\\n"] if frames else []
        lines += traceback.format_list(frames) + traceback.format_exception_only(type(e), e)
        return json.dumps({"ok": False, "error": "".join(lines).strip(), "stdout": out.getvalue()[:MAX_STDOUT]})
    finally:
        sys.stdout = old_stdout
`;

const ready = (async () => {
  const pyodide = await loadPyodide({ indexURL: "/pyodide/" });
  pyodide.runPython(HARNESS);
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
    const raw = run(data.code, data.functionName, JSON.stringify(data.args));
    postMessage({ type: "result", id: data.id, timeMs: performance.now() - start, ...JSON.parse(raw) });
  } catch (err) {
    postMessage({ type: "result", id: data.id, ok: false, error: String(err), stdout: "", timeMs: performance.now() - start });
  } finally {
    run.destroy();
  }
};
