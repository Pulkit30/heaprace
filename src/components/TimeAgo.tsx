"use client";

import { useSyncExternalStore } from "react";

const noopSubscribe = () => () => {};

function relative(iso: string): string {
  const seconds = Math.round((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 45) return "just now";
  const units: [Intl.RelativeTimeFormatUnit, number][] = [
    ["minute", 60],
    ["hour", 3600],
    ["day", 86400],
    ["month", 2592000],
    ["year", 31536000],
  ];
  const fmt = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  let chosen = units[0];
  for (const u of units) if (seconds >= u[1]) chosen = u;
  return fmt.format(-Math.round(seconds / chosen[1]), chosen[0]);
}

/** "5 minutes ago". Renders only in the browser, so server and client never disagree about the time. */
export default function TimeAgo({ iso }: { iso: string }) {
  const isClient = useSyncExternalStore(noopSubscribe, () => true, () => false);
  return (
    <time dateTime={iso} title={isClient ? new Date(iso).toLocaleString() : undefined}>
      {isClient ? relative(iso) : " "}
    </time>
  );
}
