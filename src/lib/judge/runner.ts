"use client";

import type { Problem, TestCase } from "../problems";
import { isCorrect } from "./compare";

// Phase 1 judges in the browser, so a determined user can fake a result.
// Phase 3 moves Submit to a server-side judge; Run can keep using this.

export type Verdict = "Accepted" | "Wrong Answer" | "Runtime Error" | "Time Limit Exceeded";
export type RunnerStatus = "idle" | "loading" | "ready" | "error";

/** Per-test time limit. Pyodide is roughly 2–5× slower than native CPython. */
export const TIME_LIMIT_MS = 3000;

export interface CaseResult {
  /** Position of the test in problem.tests. */
  index: number;
  test: TestCase;
  verdict: Verdict;
  actual?: unknown;
  error?: string;
  stdout: string;
  timeMs: number;
}

export interface JudgeResult {
  mode: "run" | "submit";
  verdict: Verdict;
  cases: CaseResult[];
  passed: number;
  total: number;
  timeMs: number;
}

interface WorkerResult {
  ok: boolean;
  result?: unknown;
  error?: string;
  stdout: string;
  timeMs: number;
}

class PythonRunner {
  private worker: Worker | null = null;
  private ready: Promise<void> | null = null;
  private nextId = 0;
  private listeners = new Set<(s: RunnerStatus) => void>();
  status: RunnerStatus = "idle";

  subscribe(fn: (s: RunnerStatus) => void) {
    this.listeners.add(fn);
    return () => void this.listeners.delete(fn);
  }

  private setStatus(s: RunnerStatus) {
    this.status = s;
    this.listeners.forEach((fn) => fn(s));
  }

  /** Starts the worker and downloads Python (~10 MB, cached by the browser after the first visit). */
  ensureReady(): Promise<void> {
    if (this.ready) return this.ready;
    this.setStatus("loading");
    const worker = new Worker("/pyodide-worker.js", { type: "module" });
    this.worker = worker;
    this.ready = new Promise<void>((resolve, reject) => {
      const onMessage = (e: MessageEvent) => {
        if (e.data.type === "ready") {
          worker.removeEventListener("message", onMessage);
          this.setStatus("ready");
          resolve();
        } else if (e.data.type === "init-error") {
          worker.removeEventListener("message", onMessage);
          this.reset("error");
          reject(new Error(`Python failed to load: ${e.data.error}`));
        }
      };
      worker.addEventListener("message", onMessage);
      worker.addEventListener("error", () => {
        this.reset("error");
        reject(new Error("Python failed to load. Refresh the page to try again."));
      });
    });
    return this.ready;
  }

  private reset(status: RunnerStatus) {
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
    this.setStatus(status);
  }

  /** Runs one test. Resolves "timeout" if it exceeds the limit; the worker is then killed and restarted. */
  async runOne(code: string, functionName: string, args: unknown[]): Promise<WorkerResult | "timeout"> {
    await this.ensureReady();
    const worker = this.worker!;
    const id = this.nextId++;
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        worker.removeEventListener("message", onMessage);
        this.reset("idle");
        this.ensureReady().catch(() => {}); // warm up a fresh worker for the next run
        resolve("timeout");
      }, TIME_LIMIT_MS);
      const onMessage = (e: MessageEvent) => {
        if (e.data.type !== "result" || e.data.id !== id) return;
        clearTimeout(timer);
        worker.removeEventListener("message", onMessage);
        resolve(e.data);
      };
      worker.addEventListener("message", onMessage);
      worker.postMessage({ type: "run", id, code, functionName, args });
    });
  }
}

export const runner = new PythonRunner();

/**
 * Run: all sample tests, so the user sees every result.
 * Submit: every test, stopping at the first failure (like most judges).
 */
export async function judge(
  problem: Problem,
  code: string,
  mode: "run" | "submit",
  onProgress?: (done: number, total: number) => void,
): Promise<JudgeResult> {
  const tests = problem.tests
    .map((test, index) => ({ test, index }))
    .filter(({ test }) => mode === "submit" || test.sample);
  const cases: CaseResult[] = [];

  for (const { test, index } of tests) {
    onProgress?.(cases.length, tests.length);
    const r = await runner.runOne(code, problem.functionName, test.args);
    let c: CaseResult;
    if (r === "timeout") {
      c = { index, test, verdict: "Time Limit Exceeded", stdout: "", timeMs: TIME_LIMIT_MS };
    } else if (!r.ok) {
      c = { index, test, verdict: "Runtime Error", error: r.error, stdout: r.stdout, timeMs: r.timeMs };
    } else {
      const ok = isCorrect(r.result, test.expected, problem.compare);
      c = { index, test, verdict: ok ? "Accepted" : "Wrong Answer", actual: r.result, stdout: r.stdout, timeMs: r.timeMs };
    }
    cases.push(c);
    if (mode === "submit" && c.verdict !== "Accepted") break;
  }

  const failed = cases.find((c) => c.verdict !== "Accepted");
  return {
    mode,
    verdict: failed?.verdict ?? "Accepted",
    cases,
    passed: cases.filter((c) => c.verdict === "Accepted").length,
    total: tests.length,
    timeMs: cases.reduce((sum, c) => sum + c.timeMs, 0),
  };
}
