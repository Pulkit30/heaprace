"use client";

import { useState } from "react";
import type { Problem, TestCase } from "@/lib/problems";
import { formatValue } from "@/lib/judge/compare";
import type { CaseResult, JudgeResult, Verdict } from "@/lib/judge/runner";

export type ConsoleTab = "testcases" | "result";

interface Props {
  problem: Problem;
  tab: ConsoleTab;
  onTabChange: (tab: ConsoleTab) => void;
  result: JudgeResult | null;
  /** Set while judging: how many tests have finished. */
  progress: { done: number; total: number } | null;
  error: string | null;
}

const verdictColor: Record<Verdict, string> = {
  Accepted: "text-easy",
  "Wrong Answer": "text-hard",
  "Runtime Error": "text-hard",
  "Time Limit Exceeded": "text-medium",
};

export default function Console({ problem, tab, onTabChange, result, progress, error }: Props) {
  const samples = problem.tests.filter((t) => t.sample);

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div role="tablist" className="flex shrink-0 gap-1 border-b border-line px-2">
        {(["testcases", "result"] as const).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => onTabChange(t)}
            className={`border-b-2 px-3 py-2 text-sm transition-colors ${
              tab === t ? "border-accent text-fg" : "border-transparent text-muted hover:text-fg"
            }`}
          >
            {t === "testcases" ? "Test cases" : "Result"}
          </button>
        ))}
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-4">
        {tab === "testcases" ? (
          <CasePicker
            key="samples"
            labels={samples.map((_, i) => ({ text: `Case ${i + 1}` }))}
            render={(i) => <CaseDetails problem={problem} test={samples[i]} />}
          />
        ) : (
          <ResultView problem={problem} result={result} progress={progress} error={error} />
        )}
      </div>
    </div>
  );
}

function ResultView({ problem, result, progress, error }: Omit<Props, "tab" | "onTabChange">) {
  if (progress) {
    return (
      <p className="text-sm text-muted">
        Running test {Math.min(progress.done + 1, progress.total)} of {progress.total}…
      </p>
    );
  }
  if (error) return <p className="text-sm text-hard">{error}</p>;
  if (!result) return <p className="text-sm text-muted">Run your code to see results here.</p>;

  const failed = result.cases.find((c) => c.verdict !== "Accepted");
  const title = result.mode === "submit" && result.verdict === "Accepted" ? "Accepted 🎉" : result.verdict;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h3 className={`text-lg font-semibold ${verdictColor[result.verdict]}`}>{title}</h3>
        <span className="text-sm text-muted">
          {result.passed}/{result.total} tests passed · {Math.round(result.timeMs)} ms
          {result.mode === "submit" && " · includes hidden tests"}
        </span>
      </div>

      {result.mode === "run" ? (
        <CasePicker
          key={`${result.mode}-${result.timeMs}`}
          initial={Math.max(0, result.cases.findIndex((c) => c.verdict !== "Accepted"))}
          labels={result.cases.map((c, i) => ({ text: `Case ${i + 1}`, ok: c.verdict === "Accepted" }))}
          render={(i) => <CaseResultDetails problem={problem} c={result.cases[i]} />}
        />
      ) : failed ? (
        <>
          <p className="mb-3 text-sm text-muted">
            Failed on test {failed.index + 1}
            {failed.test.sample ? " (a sample test)" : " (a hidden test)"}:
          </p>
          <CaseResultDetails problem={problem} c={failed} />
        </>
      ) : (
        <p className="text-sm text-muted">Your solution passed every test. It&apos;s marked solved in the problem list.</p>
      )}
    </div>
  );
}

function CasePicker({
  labels,
  render,
  initial = 0,
}: {
  labels: { text: string; ok?: boolean }[];
  render: (i: number) => React.ReactNode;
  initial?: number;
}) {
  const [active, setActive] = useState(initial);
  return (
    <>
      <div className="mb-4 flex flex-wrap gap-2">
        {labels.map((l, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-sm transition-colors ${
              active === i ? "bg-surface-2 text-fg" : "text-muted hover:bg-surface-2/60"
            }`}
          >
            {l.ok !== undefined && (
              <span className={`h-1.5 w-1.5 rounded-full ${l.ok ? "bg-easy" : "bg-hard"}`} aria-hidden />
            )}
            {l.text}
            {l.ok === false && <span className="sr-only">(failed)</span>}
          </button>
        ))}
      </div>
      {labels.length > 0 && render(active)}
    </>
  );
}

function Field({ label, value, tone }: { label: string; value: string; tone?: "error" | "ok" }) {
  return (
    <div className="mb-3">
      <div className="mb-1 text-xs text-muted">{label}</div>
      <pre
        className={`overflow-x-auto whitespace-pre-wrap break-words rounded-md bg-surface-2 px-3 py-2 font-mono text-[13px] ${
          tone === "error" ? "text-hard" : ""
        }`}
      >
        {value}
      </pre>
    </div>
  );
}

function CaseDetails({ problem, test }: { problem: Problem; test: TestCase }) {
  return (
    <>
      {problem.params.map((name, i) => (
        <Field key={name} label={name} value={formatValue(test.args[i])} />
      ))}
    </>
  );
}

function CaseResultDetails({ problem, c }: { problem: Problem; c: CaseResult }) {
  return (
    <>
      <CaseDetails problem={problem} test={c.test} />
      {c.verdict === "Runtime Error" && <Field label="Error" value={c.error ?? "Unknown error"} tone="error" />}
      {c.verdict === "Time Limit Exceeded" && (
        <Field label="Error" value="Your code took too long. Look for an infinite loop or a slower-than-needed approach." tone="error" />
      )}
      {c.verdict !== "Runtime Error" && c.verdict !== "Time Limit Exceeded" && (
        <Field label="Your output" value={formatValue(c.actual)} />
      )}
      <Field label="Expected" value={formatValue(c.test.expected)} />
      {c.stdout && <Field label="Stdout (your print statements)" value={c.stdout} />}
    </>
  );
}
