import { getCurrentUser } from "@/lib/auth/server";
import { getRaceState, normalizeCode, type RaceState } from "@/lib/race";

// One long-lived Server-Sent Events connection per race page, instead of the browser polling.
// The server checks the room and pushes a message only when something changed. The stream closes
// before the platform's time limit; EventSource reconnects on its own (about once a minute).
export const maxDuration = 60;

const STREAM_MS = 50_000;
const HEARTBEAT_MS = 15_000;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Everything except the server clock, so an unchanged room isn't re-sent every check. */
const fingerprint = (s: RaceState) => JSON.stringify({ ...s, serverNow: null });

export async function GET(req: Request, ctx: RouteContext<"/api/race/[code]/events">) {
  const user = await getCurrentUser();
  if (!user) return new Response("Unauthorized", { status: 401 });
  const code = normalizeCode((await ctx.params).code);
  const first = code ? await getRaceState(code, user.id) : null;
  if (!code || !first) return new Response("Not found", { status: 404 });

  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const write = (chunk: string) => {
        try {
          controller.enqueue(encoder.encode(chunk));
          return true;
        } catch {
          return false; // the browser went away
        }
      };

      let last = fingerprint(first);
      let lastWrite = Date.now();
      let phase = first.phase;
      write(`retry: 2000\ndata: ${JSON.stringify(first)}\n\n`);

      const deadline = Date.now() + STREAM_MS;
      while (!req.signal.aborted && phase !== "finished" && Date.now() < deadline) {
        // Check faster around the countdown so the problem appears the moment the race starts.
        await sleep(phase === "countdown" ? 500 : 1500);
        if (req.signal.aborted) break;

        let state: RaceState | null;
        try {
          state = await getRaceState(code, user.id);
        } catch {
          continue; // database hiccup: try again next tick
        }
        if (!state) {
          write(`event: gone\ndata: {}\n\n`);
          break;
        }
        phase = state.phase;

        const fp = fingerprint(state);
        if (fp !== last) {
          last = fp;
          lastWrite = Date.now();
          if (!write(`data: ${JSON.stringify(state)}\n\n`)) break;
        } else if (Date.now() - lastWrite > HEARTBEAT_MS) {
          lastWrite = Date.now();
          if (!write(`: keep-alive\n\n`)) break;
        }
      }
      try {
        controller.close();
      } catch {
        // already closed
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
