import { getCurrentUser } from "@/lib/auth/server";
import { getRaceState, normalizeCode } from "@/lib/race";

/** Polled by the race page every couple of seconds for the lobby, countdown and live standings. */
export async function GET(_req: Request, ctx: RouteContext<"/api/race/[code]">) {
  const user = await getCurrentUser();
  if (!user) return Response.json({ error: "Unauthorized" }, { status: 401 });

  const code = normalizeCode((await ctx.params).code);
  const state = code ? await getRaceState(code, user.id) : null;
  if (!state) return Response.json({ error: "Not found" }, { status: 404 });

  return Response.json(state, { headers: { "Cache-Control": "no-store" } });
}
