import "server-only";
import { createNeonAuth } from "@neondatabase/auth/next/server";
import { cookies } from "next/headers";

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
  const { data: session } = await auth.getSession();
  return session?.user ?? null;
}

/** Only allow redirects to paths on this site, never to another origin. */
export function safeNext(next: unknown, fallback = "/problems"): string {
  return typeof next === "string" && next.startsWith("/") && !next.startsWith("//") ? next : fallback;
}
