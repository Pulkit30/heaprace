import Link from "next/link";
import Logo from "./Logo";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-20 h-14 shrink-0 border-b border-line bg-bg/90 backdrop-blur">
      <nav className="mx-auto flex h-full max-w-[1600px] items-center gap-6 px-4">
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
        <button
          disabled
          title="Accounts arrive in Phase 2"
          className="cursor-not-allowed rounded-md border border-line px-3 py-1.5 text-sm text-muted"
        >
          Sign in
        </button>
      </nav>
    </header>
  );
}
