"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import type { Problem } from "@/lib/problems";
import { judge, runner, type JudgeResult, type RunnerStatus } from "@/lib/judge/runner";
import { clearCode } from "@/lib/drafts";
import type { SubmissionRow } from "@/lib/queries";
import { submitSolution } from "@/app/problems/[slug]/actions";
import type { SubmitResult } from "@/lib/submit";
import type { EditorInstance } from "./CodeEditor";
import EditorPlaceholder from "./EditorPlaceholder";
import Console, { type ConsoleTab } from "./Console";
import Description from "./Description";
import SubmissionsPanel from "./SubmissionsPanel";
import { useSplit } from "./useSplit";

const CodeEditor = dynamic(() => import("./CodeEditor"), { ssr: false, loading: EditorPlaceholder });

function useRunnerStatus(): RunnerStatus {
  return useSyncExternalStore(
    (fn) => runner.subscribe(fn),
    () => runner.status,
    () => "idle",
  );
}

export type SaveState = "saved" | "signed-out" | null;

interface Props {
  /** The problem with its sample tests only; hidden tests stay on the server. */
  problem: Problem;
  signedIn: boolean;
  initialSubmissions: SubmissionRow[];
  /** Overrides how Submit is judged (race mode passes its own). Defaults to the practice submit. */
  submit?: (code: string) => Promise<SubmitResult>;
  /** Extra left-panel tab, e.g. the race leaderboard. */
  extraTab?: { label: string; content: React.ReactNode };
  /** Where the code draft is saved in the browser. Defaults to the problem slug; races use their own key. */
  draftKey?: string;
  /** Desktop height of the workspace. Race mode subtracts its timer bar. */
  heightClass?: string;
}

export default function Workspace({
  problem,
  signedIn,
  initialSubmissions,
  submit,
  extraTab,
  draftKey = problem.slug,
  heightClass = "lg:h-[calc(100dvh-3.5rem)]",
}: Props) {
  const editorRef = useRef<EditorInstance | null>(null);
  const rowRef = useRef<HTMLDivElement>(null);
  const colRef = useRef<HTMLDivElement>(null);
  const [leftPct, leftHandle] = useSplit(rowRef, "x", 42, [25, 70]);
  const [topPct, topHandle] = useSplit(colRef, "y", 62, [25, 85]);

  const status = useRunnerStatus();
  const [tab, setTab] = useState<ConsoleTab>("testcases");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);
  const [result, setResult] = useState<JudgeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [leftTab, setLeftTab] = useState<"description" | "submissions" | "extra">("description");
  const [submissions, setSubmissions] = useState(initialSubmissions);
  const [saveState, setSaveState] = useState<SaveState>(null);
  const solved = submissions.some((s) => s.verdict === "Accepted");
  const signInHref = `/auth/sign-in?next=${encodeURIComponent(`/problems/${problem.slug}`)}`;

  // Start downloading Python as soon as the page opens, so the first Run is fast.
  useEffect(() => {
    runner.ensureReady().catch(() => {});
  }, []);

  async function execute(mode: "run" | "submit") {
    const code = editorRef.current?.getValue();
    if (busy || code === undefined) return;
    setBusy(true);
    setTab("result");
    setError(null);
    setResult(null);
    setSaveState(null);
    setProgress({ done: 0, total: 0 });
    try {
      if (mode === "run") {
        // Run: sample tests in the browser, instant and free.
        setResult(await judge(problem, code, "run", (done, total) => setProgress({ done, total })));
      } else if (!signedIn) {
        setSaveState("signed-out");
      } else {
        // Submit: every test, judged on the server.
        const res = await (submit ?? ((c: string) => submitSolution({ slug: problem.slug, code: c })))(code);
        if (res.ok) {
          setResult(res.result);
          setSubmissions((prev) => [res.submission, ...prev]);
          setSaveState("saved");
        } else if (res.reason === "signed-out") {
          setSaveState("signed-out");
        } else {
          setError(res.message);
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setProgress(null);
      setBusy(false);
    }
  }

  // Keyboard shortcuts call the latest execute() through a ref, since Monaco registers them once.
  const executeRef = useRef(execute);
  useEffect(() => {
    executeRef.current = execute;
  });

  function loadCode(code: string) {
    if (!confirm("Replace the code in the editor with this submission?")) return;
    editorRef.current?.setValue(code);
  }

  function resetCode() {
    if (!confirm("Reset to the starter code? Your current code will be lost.")) return;
    clearCode(draftKey);
    editorRef.current?.setValue(problem.starterCode);
  }

  const pythonLabel: Record<RunnerStatus, string> = {
    idle: "Python",
    loading: "Loading Python…",
    ready: "Python ready",
    error: "Python failed to load",
  };

  return (
    <div
      ref={rowRef}
      style={{ "--left": `${leftPct}%`, "--top": `${topPct}%` } as React.CSSProperties}
      className={`flex min-h-0 flex-1 flex-col gap-2 p-2 lg:grid ${heightClass} lg:grid-cols-[var(--left)_6px_minmax(0,1fr)] lg:gap-0`}
    >
      <section className="min-h-0 overflow-auto rounded-lg border border-line bg-surface">
        <div className="sticky top-0 z-10 flex items-center gap-1 border-b border-line bg-surface px-2 text-sm">
          <Link href="/problems" className="px-2 py-2 text-muted hover:text-fg" aria-label="Back to problems">
            ←
          </Link>
          {(extraTab ? (["description", "extra", "submissions"] as const) : (["description", "submissions"] as const)).map(
            (t) => (
              <button
                key={t}
                onClick={() => setLeftTab(t)}
                aria-pressed={leftTab === t}
                className={`border-b-2 px-3 py-2 transition-colors ${
                  leftTab === t ? "border-accent-fill text-fg" : "border-transparent text-muted hover:text-fg"
                }`}
              >
                {t === "description"
                  ? "Description"
                  : t === "extra"
                    ? extraTab?.label
                    : `Submissions${submissions.length ? ` (${submissions.length})` : ""}`}
              </button>
            ),
          )}
          {solved && <span className="ml-auto pr-2 text-xs font-medium text-easy">Solved ✓</span>}
        </div>
        {leftTab === "description" ? (
          <Description problem={problem} />
        ) : leftTab === "extra" ? (
          extraTab?.content
        ) : (
          <SubmissionsPanel
            submissions={submissions}
            signedIn={signedIn}
            signInHref={signInHref}
            onLoadCode={loadCode}
          />
        )}
      </section>

      <div {...leftHandle} className="hidden cursor-col-resize items-center justify-center lg:flex">
        <div className="h-10 w-0.5 rounded bg-line" />
      </div>

      <div
        ref={colRef}
        className="flex min-h-0 flex-col gap-2 lg:grid lg:grid-rows-[var(--top)_6px_minmax(0,1fr)] lg:gap-0"
      >
        <section className="flex h-[60vh] min-h-0 flex-col overflow-hidden rounded-lg border border-line bg-surface lg:h-auto">
          <div className="flex shrink-0 items-center gap-3 border-b border-line px-3 py-2 text-sm">
            <span className="font-medium">Python 3</span>
            <span className={`flex items-center gap-1.5 text-xs ${status === "error" ? "text-hard" : "text-muted"}`}>
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  status === "ready" ? "bg-easy" : status === "error" ? "bg-hard" : "animate-pulse bg-medium"
                }`}
                aria-hidden
              />
              {pythonLabel[status]}
            </span>
            <button onClick={resetCode} className="ml-auto text-xs text-muted hover:text-fg">
              Reset code
            </button>
          </div>
          <div className="min-h-0 flex-1">
            <CodeEditor
              slug={draftKey}
              starterCode={problem.starterCode}
              onMount={(editor, monaco) => {
                editorRef.current = editor;
                const { CtrlCmd, Shift } = monaco.KeyMod;
                editor.addCommand(CtrlCmd | monaco.KeyCode.Enter, () => executeRef.current("run"));
                editor.addCommand(CtrlCmd | Shift | monaco.KeyCode.Enter, () => executeRef.current("submit"));
              }}
            />
          </div>
        </section>

        <div {...topHandle} className="hidden cursor-row-resize items-center justify-center lg:flex">
          <div className="h-0.5 w-10 rounded bg-line" />
        </div>

        <section className="flex min-h-[18rem] flex-col overflow-hidden rounded-lg border border-line bg-surface lg:min-h-0">
          <div className="min-h-0 flex-1">
            <Console
              problem={problem}
              tab={tab}
              onTabChange={setTab}
              result={result}
              progress={progress}
              error={error}
              saveState={saveState}
              signInHref={signInHref}
            />
          </div>
          <div className="flex shrink-0 items-center justify-end gap-2 border-t border-line px-3 py-2">
            <span className="mr-auto hidden text-xs text-muted sm:inline">⌘/Ctrl + Enter to run</span>
            <button
              onClick={() => execute("run")}
              disabled={busy}
              className="rounded-md bg-surface-2 px-4 py-1.5 text-sm font-medium transition-colors hover:bg-line disabled:opacity-50"
            >
              Run
            </button>
            <button
              onClick={() => execute("submit")}
              disabled={busy}
              className="rounded-md bg-accent-fill px-4 py-1.5 text-sm font-medium text-black transition-colors hover:bg-accent-strong disabled:opacity-50"
            >
              Submit
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
