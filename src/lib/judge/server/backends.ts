import "server-only";
import { spawn } from "node:child_process";

export interface ExecRequest {
  source: string;
  stdin: string;
  /** Limit for the whole program (all tests). */
  wallTimeSec: number;
  memoryKb: number;
}

export interface ExecResult {
  status: "finished" | "time-limit" | "crashed";
  stdout: string;
  stderr: string;
  /** Human-readable reason when status is "crashed", e.g. "Memory limit exceeded". */
  message?: string;
}

export class JudgeUnavailableError extends Error {}

export interface JudgeBackend {
  name: string;
  execute(req: ExecRequest): Promise<ExecResult>;
}

const b64 = (s: string) => Buffer.from(s, "utf8").toString("base64");
const unb64 = (s: string | null | undefined) => (s ? Buffer.from(s, "base64").toString("utf8") : "");

/**
 * Judge0 (https://judge0.com): self-hosted (JUDGE0_URL=http://your-server:2358, optional JUDGE0_AUTH_TOKEN)
 * or the hosted API on RapidAPI (JUDGE0_URL=https://judge0-ce.p.rapidapi.com, JUDGE0_RAPIDAPI_KEY).
 */
function judge0Backend(url: string): JudgeBackend {
  const base = url.replace(/\/+$/, "");
  const languageId = Number(process.env.JUDGE0_PYTHON_LANGUAGE_ID ?? 71); // 71 = Python 3 on Judge0 CE
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (process.env.JUDGE0_RAPIDAPI_KEY) {
    headers["X-RapidAPI-Key"] = process.env.JUDGE0_RAPIDAPI_KEY;
    headers["X-RapidAPI-Host"] = new URL(base).host;
  } else if (process.env.JUDGE0_AUTH_TOKEN) {
    headers["X-Auth-Token"] = process.env.JUDGE0_AUTH_TOKEN;
  }

  return {
    name: "judge0",
    async execute(req) {
      let res: Response;
      try {
        res = await fetch(`${base}/submissions?base64_encoded=true&wait=true`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            language_id: languageId,
            source_code: b64(req.source),
            stdin: b64(req.stdin),
            cpu_time_limit: req.wallTimeSec,
            wall_time_limit: req.wallTimeSec + 2,
            memory_limit: req.memoryKb,
          }),
          signal: AbortSignal.timeout((req.wallTimeSec + 15) * 1000),
          cache: "no-store",
        });
      } catch (e) {
        throw new JudgeUnavailableError(`Judge0 is unreachable: ${e instanceof Error ? e.message : e}`);
      }
      if (!res.ok) {
        throw new JudgeUnavailableError(`Judge0 returned HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);
      }
      const body = (await res.json()) as {
        status?: { id: number; description: string };
        stdout?: string | null;
        stderr?: string | null;
        compile_output?: string | null;
        message?: string | null;
      };
      const statusId = body.status?.id ?? 0;
      const stdout = unb64(body.stdout);
      const stderr = unb64(body.stderr) || unb64(body.compile_output);
      // 3 = ran to completion, 5 = time limit, 7–12 = runtime errors (signals, non-zero exit, memory).
      if (statusId === 3) return { status: "finished", stdout, stderr };
      if (statusId === 5) return { status: "time-limit", stdout, stderr };
      if (statusId >= 6 && statusId <= 12) {
        return { status: "crashed", stdout, stderr, message: body.status?.description ?? "Runtime error" };
      }
      throw new JudgeUnavailableError(
        `Judge0 status ${statusId} (${body.status?.description ?? "unknown"}): ${unb64(body.message) || ""}`,
      );
    },
  };
}

/**
 * Development only: runs the program with the local python3. Your own code on your own machine,
 * so there's no sandbox. Refuses to run in production.
 */
const localPythonBackend: JudgeBackend = {
  name: "local-python",
  execute(req) {
    if (process.env.NODE_ENV === "production") {
      return Promise.reject(new JudgeUnavailableError("The local judge is disabled in production. Set JUDGE0_URL."));
    }
    return new Promise((resolve, reject) => {
      const child = spawn(process.env.LOCAL_PYTHON ?? "python3", ["-I", "-c", req.source], {
        stdio: ["pipe", "pipe", "pipe"],
      });
      let stdout = "";
      let stderr = "";
      let timedOut = false;
      const timer = setTimeout(() => {
        timedOut = true;
        child.kill("SIGKILL");
      }, req.wallTimeSec * 1000);
      child.stdout.on("data", (d) => (stdout += d));
      child.stderr.on("data", (d) => (stderr = (stderr + d).slice(-20_000)));
      child.on("error", (e) => {
        clearTimeout(timer);
        reject(new JudgeUnavailableError(`Couldn't start python3 for the local judge: ${e.message}`));
      });
      child.on("close", (code) => {
        clearTimeout(timer);
        if (timedOut) resolve({ status: "time-limit", stdout, stderr });
        else if (code === 0) resolve({ status: "finished", stdout, stderr });
        else resolve({ status: "crashed", stdout, stderr, message: `Process exited with code ${code}` });
      });
      child.stdin.end(req.stdin);
    });
  },
};

export function getBackend(): JudgeBackend {
  const url = process.env.JUDGE0_URL;
  return url ? judge0Backend(url) : localPythonBackend;
}
