"use client";

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import type { RaceState } from "@/lib/race";

/**
 * Live race state over one Server-Sent Events connection (/api/race/[code]/events). The server pushes
 * a message only when the room changes; EventSource reconnects by itself when the stream is recycled.
 * `refresh` does a single fetch, used right after an action (start, submit) for an instant update.
 */
export function useRace(initial: RaceState) {
  const [state, setState] = useState(initial);
  const [offsetMs, setOffsetMs] = useState(0);
  const [lost, setLost] = useState(false);
  const code = initial.code;
  const initiallyFinished = initial.phase === "finished";

  const apply = useCallback((next: RaceState) => {
    setOffsetMs(Date.parse(next.serverNow) - Date.now());
    setState(next);
  }, []);

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`/api/race/${code}`, { cache: "no-store" });
      if (res.ok) apply((await res.json()) as RaceState);
      else if (res.status === 404) setLost(true);
    } catch {
      // Network blip: the event stream will catch up.
    }
  }, [code, apply]);

  useEffect(() => {
    if (initiallyFinished) return;
    const events = new EventSource(`/api/race/${code}/events`);
    events.onmessage = (e) => {
      const next = JSON.parse(e.data) as RaceState;
      apply(next);
      if (next.phase === "finished") events.close(); // nothing more will change
    };
    events.addEventListener("gone", () => {
      setLost(true);
      events.close();
    });
    events.onerror = () => {
      // A refused reconnect (e.g. 404 after the host cancelled) leaves the stream closed: check once.
      if (events.readyState === EventSource.CLOSED) void refresh();
    };
    return () => events.close();
  }, [code, initiallyFinished, apply, refresh]);

  return { state, offsetMs, refresh, lost };
}

const TICK_MS = 250;
const subscribeTick = (onTick: () => void) => {
  const id = setInterval(onTick, TICK_MS);
  return () => clearInterval(id);
};
const tickSnapshot = () => Math.floor(Date.now() / TICK_MS) * TICK_MS;

/** Current time on the server's clock, ticking 4×/s. Use it only in small components (timers). */
export function useServerNow(offsetMs: number): number {
  return useSyncExternalStore(subscribeTick, tickSnapshot, () => 0) + offsetMs;
}

export function formatClock(ms: number): string {
  const total = Math.max(0, Math.ceil(ms / 1000));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const mm = String(m).padStart(h ? 2 : 1, "0");
  return `${h ? `${h}:` : ""}${mm}:${String(s).padStart(2, "0")}`;
}
