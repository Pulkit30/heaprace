"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

/**
 * Stores the browser's timezone in a cookie so the server can decide which calendar day a submission
 * belongs to. Refreshes once when the timezone is first learned or changes (e.g. after travelling).
 */
export default function TimezoneSync() {
  const router = useRouter();

  useEffect(() => {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const current = document.cookie.match(/(?:^|;\s*)tz=([^;]*)/)?.[1];
    if (!tz || (current && decodeURIComponent(current) === tz)) return;
    document.cookie = `tz=${encodeURIComponent(tz)}; path=/; max-age=31536000; samesite=lax`;
    router.refresh();
  }, [router]);

  return null;
}
