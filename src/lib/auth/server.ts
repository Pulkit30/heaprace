import "server-only";
import { createNeonAuth } from "@neondatabase/auth/next/server";
import { cookies } from "next/headers";
import { unstable_rethrow } from "next/navigation";

// Neon Auth (Managed Better Auth). Users and sessions live in the neon_auth schema of our database.
export const auth = createNeonAuth({
  baseUrl: process.env.NEON_AUTH_BASE_URL!,
  cookies: { secret: process.env.NEON_AUTH_COOKIE_SECRET! },
});

export type SessionUser = { id: string; name: string; email: string; image?: string | null };

/** The signed-in user, or null. Reading the session makes the calling page render per request. */
export async function getCurrentUser(): Promise<SessionUser | null> {
  // Tell Next.js this render depends on the request before the SDK reads cookies itself.
  await cookies();
  try {
    const { data: session } = await auth.getSession();
    return session?.user ?? null;
  } catch (error) {
    // Next.js's own control-flow signals (redirect, notFound, dynamic rendering) must pass through.
    unstable_rethrow(error);
    // Anything else, e.g. a stale session whose cookie can't be updated while a page renders,
    // means "not signed in" rather than a crashed page. proxy.ts refreshes cookies before rendering.
    console.warn("[auth] getSession failed; treating the visitor as signed out:", error instanceof Error ? error.message : error);
    return null;
  }
}

/** Only allow redirects to paths on this site, never to another origin. */
export function safeNext(next: unknown, fallback = "/problems"): string {
  return typeof next === "string" && next.startsWith("/") && !next.startsWith("//") ? next : fallback;
}
