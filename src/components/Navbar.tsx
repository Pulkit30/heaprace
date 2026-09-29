import Link from "next/link";
import { getCurrentUser } from "@/lib/auth/server";
import Logo from "./Logo";
import ThemeToggle from "./ThemeToggle";
import UserMenu from "./UserMenu";

export default async function Navbar() {
  const user = await getCurrentUser();

  return (
    <header className="sticky top-0 z-20 h-14 shrink-0 border-b border-line bg-surface">
      <nav className="mx-auto flex h-full max-w-[1600px] items-center gap-5 px-4">
        <Link href="/" className="text-fg">
          <Logo />
        </Link>
        <Link href="/problems" className="text-sm text-muted transition-colors hover:text-fg">
          Problems
        </Link>
        <span className="hidden text-sm text-muted/60 sm:inline" title="Coming in Phase 4">
          Race <span className="ml-1 rounded bg-surface-2 px-1.5 py-0.5 text-[10px] uppercase">soon</span>
        </span>
        <span className="ml-auto" />
        <ThemeToggle />
        {user ? (
          <UserMenu name={user.name || user.email} email={user.email} image={user.image ?? null} />
        ) : (
          <div className="flex items-center gap-2">
            <Link
              href="/auth/sign-in"
              className="rounded-md px-3 py-1.5 text-sm text-muted transition-colors hover:text-fg"
            >
              Sign in
            </Link>
            <Link
              href="/auth/sign-up"
              className="hidden rounded-md bg-accent-fill px-3 py-1.5 text-sm font-medium text-black transition-colors hover:bg-accent-strong sm:inline-block"
            >
              Sign up
            </Link>
          </div>
        )}
      </nav>
    </header>
  );
}
