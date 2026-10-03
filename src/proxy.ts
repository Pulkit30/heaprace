import { NextResponse, type NextRequest } from "next/server";
import { auth } from "@/lib/auth/server";

const LOGIN_URL = "/auth/sign-in";
const authMiddleware = auth.middleware({ loginUrl: LOGIN_URL });

/** Pages that require an account; signed-out visitors are sent to the sign-in page. */
const PROTECTED = ["/submissions", "/progress"];
const isProtected = (path: string) => PROTECTED.some((p) => path === p || path.startsWith(`${p}/`));

/**
 * Runs Neon Auth on every page *before* it renders. That's the only place session cookies may be
 * refreshed or cleared (e.g. after a user is deleted); doing it during rendering crashes the page.
 * Protected pages keep the login redirect. On public pages a signed-out visitor is let through,
 * while any cookie updates (such as clearing a stale session) are kept.
 * Server Actions and data queries still check the session themselves; this is not the only guard.
 */
export default async function proxy(request: NextRequest) {
  const response = await authMiddleware(request);
  if (isProtected(request.nextUrl.pathname)) return response;

  const location = response.headers.get("location");
  const isLoginRedirect = location !== null && new URL(location, request.url).pathname === LOGIN_URL;
  if (!isLoginRedirect) return response; // includes the OAuth callback redirect

  const passThrough = NextResponse.next();
  for (const cookie of response.headers.getSetCookie()) passThrough.headers.append("Set-Cookie", cookie);
  return passThrough;
}

export const config = {
  // Every page, but not API routes, Next.js assets, or static files like the Python runtime.
  matcher: ["/((?!api/|_next/|favicon.ico|pyodide/|pyodide-worker.js|judge-harness.py|.*\\.(?:svg|png|jpg|ico|js|css|wasm|zip|json)$).*)"],
};
