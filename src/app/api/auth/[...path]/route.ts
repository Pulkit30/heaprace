import { auth } from "@/lib/auth/server";

// Proxies browser auth requests (sign in, Google callback, session refresh) to Neon Auth.
export const { GET, POST, PUT, DELETE, PATCH } = auth.handler();
