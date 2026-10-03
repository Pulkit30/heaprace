"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { signOut } from "@/app/auth/actions";
import { claimUserData, clearUserData } from "@/lib/drafts";

interface Props {
  id: string;
  name: string;
  email: string;
  image: string | null;
}

export default function UserMenu({ id, name, email, image }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // A different account signing in on this browser starts with a clean editor and hint progress.
  useEffect(() => claimUserData(id), [id]);

  useEffect(() => {
    if (!open) return;
    const close = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === "Escape" : !ref.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open]);

  const initial = name.trim().charAt(0).toUpperCase() || "?";

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label="Account menu"
        className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-accent-fill text-sm font-semibold text-on-accent"
      >
        {image ? (
          // eslint-disable-next-line @next/next/no-img-element -- avatar from the auth provider's domain
          <img src={image} alt="" className="h-full w-full object-cover" referrerPolicy="no-referrer" />
        ) : (
          initial
        )}
      </button>
      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-56 overflow-hidden rounded-lg border border-line bg-surface shadow-lg"
        >
          <div className="border-b border-line px-4 py-3">
            <p className="truncate text-sm font-medium">{name}</p>
            <p className="truncate text-xs text-muted">{email}</p>
          </div>
          <Link
            href={`/u/${id}`}
            role="menuitem"
            onClick={() => setOpen(false)}
            className="block px-4 py-2 text-sm transition-colors hover:bg-surface-2"
          >
            My profile
          </Link>
          <Link
            href="/progress"
            role="menuitem"
            onClick={() => setOpen(false)}
            className="block px-4 py-2 text-sm transition-colors hover:bg-surface-2"
          >
            My progress
          </Link>
          <Link
            href="/submissions"
            role="menuitem"
            onClick={() => setOpen(false)}
            className="block px-4 py-2 text-sm transition-colors hover:bg-surface-2"
          >
            My submissions
          </Link>
          <form action={signOut} onSubmit={clearUserData}>
            <button role="menuitem" className="w-full px-4 py-2 text-left text-sm text-muted transition-colors hover:bg-surface-2 hover:text-fg">
              Sign out
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
