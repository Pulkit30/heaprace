import Link from "next/link";
import { getCurrentUser } from "@/lib/auth/server";
import { getActivity } from "@/lib/queries";
import { computeStreaks, todayIn } from "@/lib/streak";
import { getUserTimeZone } from "@/lib/timezone";
import Logo from "./Logo";
import StreakBadge from "./progress/StreakBadge";
import ThemeToggle from "./ThemeToggle";
import UserMenu from "./UserMenu";

export default async function Navbar() {
  const user = await getCurrentUser();
  let streak = null;
  if (user) {
    const timeZone = await getUserTimeZone();
    streak = computeStreaks(await getActivity(user.id, timeZone), todayIn(timeZone));
  }

  return (
    <header className="sticky top-0 z-20 h-14 shrink-0 border-b border-line bg-surface">
      <nav className="mx-auto flex h-full max-w-[1600px] items-center gap-5 px-4">
        <Link href="/" className="text-fg">
          <Logo />
        </Link>
        <Link href="/problems" className="text-sm text-muted transition-colors hover:text-fg">
          Problems
        </Link>
        <Link href="/roadmap" className="text-sm text-muted transition-colors hover:text-fg">
          Roadmap
        </Link>
        <Link href="/race" className="text-sm text-muted transition-colors hover:text-fg">
          Race
        </Link>
        <span className="ml-auto" />
        <ThemeToggle />
        {streak && <StreakBadge current={streak.current} solvedToday={streak.solvedToday} />}
        {user ? (
          <UserMenu id={user.id} name={user.name || user.email} email={user.email} image={user.image ?? null} />
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
