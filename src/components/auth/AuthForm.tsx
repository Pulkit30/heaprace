"use client";

import Link from "next/link";
import { useActionState, useState } from "react";
import { signInWithEmail, signUpWithEmail } from "@/app/auth/actions";
import { authClient } from "@/lib/auth/client";

const inputClass =
  "w-full rounded-md border border-line bg-surface-2 px-3 py-2 text-sm outline-none placeholder:text-muted focus:border-accent-fill";

export default function AuthForm({ mode, next }: { mode: "sign-in" | "sign-up"; next: string }) {
  const isSignUp = mode === "sign-up";
  const [state, formAction, pending] = useActionState(isSignUp ? signUpWithEmail : signInWithEmail, null);
  const [googleError, setGoogleError] = useState<string | null>(null);
  const [googlePending, setGooglePending] = useState(false);

  async function signInWithGoogle() {
    setGoogleError(null);
    setGooglePending(true);
    const { error } = await authClient.signIn.social({
      provider: "google",
      callbackURL: `${window.location.origin}${next}`,
    });
    if (error) {
      setGoogleError(error.message || "Google sign-in failed. Try again.");
      setGooglePending(false);
    }
  }

  const otherHref = `${isSignUp ? "/auth/sign-in" : "/auth/sign-up"}${next !== "/problems" ? `?next=${encodeURIComponent(next)}` : ""}`;
  const error = state?.error ?? googleError;

  return (
    <div className="w-full max-w-sm rounded-xl border border-line bg-surface p-6 sm:p-8">
      <h1 className="text-xl font-semibold tracking-tight">{isSignUp ? "Create your account" : "Welcome back"}</h1>
      <p className="mt-1 text-sm text-muted">
        {isSignUp ? "Save your submissions and track what you've solved." : "Sign in to keep climbing."}
      </p>

      <button
        type="button"
        onClick={signInWithGoogle}
        disabled={googlePending || pending}
        className="mt-6 flex w-full items-center justify-center gap-2 rounded-md border border-line bg-surface-2 px-3 py-2 text-sm font-medium transition-colors hover:bg-line disabled:opacity-50"
      >
        <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
          <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z" />
          <path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
          <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z" />
          <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z" />
        </svg>
        {googlePending ? "Redirecting…" : "Continue with Google"}
      </button>

      <div className="my-5 flex items-center gap-3 text-xs text-muted">
        <span className="h-px flex-1 bg-line" />
        or use email
        <span className="h-px flex-1 bg-line" />
      </div>

      <form action={formAction} className="space-y-4">
        <input type="hidden" name="next" value={next} />
        {isSignUp && (
          <label className="block">
            <span className="mb-1.5 block text-sm">Name</span>
            <input name="name" required autoComplete="name" placeholder="Ada Lovelace" className={inputClass} />
          </label>
        )}
        <label className="block">
          <span className="mb-1.5 block text-sm">Email</span>
          <input name="email" type="email" required autoComplete="email" placeholder="you@example.com" className={inputClass} />
        </label>
        <label className="block">
          <span className="mb-1.5 block text-sm">Password</span>
          <input
            name="password"
            type="password"
            required
            minLength={isSignUp ? 8 : undefined}
            autoComplete={isSignUp ? "new-password" : "current-password"}
            placeholder={isSignUp ? "At least 8 characters" : "Your password"}
            className={inputClass}
          />
        </label>

        {error && (
          <p role="alert" className="rounded-md border border-hard/30 bg-hard/10 px-3 py-2 text-sm text-hard">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={pending || googlePending}
          className="w-full rounded-md bg-accent-fill px-3 py-2 text-sm font-medium text-black transition-colors hover:bg-accent-strong disabled:opacity-50"
        >
          {pending ? (isSignUp ? "Creating account…" : "Signing in…") : isSignUp ? "Create account" : "Sign in"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-muted">
        {isSignUp ? "Already have an account? " : "New to HeapRace? "}
        <Link href={otherHref} className="text-accent hover:underline">
          {isSignUp ? "Sign in" : "Create an account"}
        </Link>
      </p>
    </div>
  );
}
