import { auth } from "@/lib/auth/server";

// Sends signed-out visitors on protected pages to the sign-in page.
// Server Actions and data queries check the session themselves too; this is only the page redirect.
export default auth.middleware({ loginUrl: "/auth/sign-in" });

export const config = {
  matcher: ["/submissions/:path*"],
};
