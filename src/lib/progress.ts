"use client";

import { useMemo, useSyncExternalStore } from "react";

// Phase 1 keeps progress and code in localStorage. Phase 2 replaces this with the database.

export type ProblemStatus = "solved" | "attempted";

const PROGRESS_KEY = "heaprace:progress";
const codeKey = (slug: string) => `heaprace:code:${slug}`;
const CHANGE_EVENT = "heaprace:progress-change";

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // Storage full or blocked (private mode): progress just won't persist.
  }
}

export function loadCode(slug: string): string | null {
  return read(codeKey(slug));
}

export function saveCode(slug: string, code: string) {
  write(codeKey(slug), code);
}

export function clearCode(slug: string) {
  write(codeKey(slug), null);
}

function parseProgress(raw: string | null): Record<string, ProblemStatus> {
  try {
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

/** Records a submission. A solved problem stays solved even if a later submission fails. */
export function recordSubmission(slug: string, accepted: boolean) {
  const progress = parseProgress(read(PROGRESS_KEY));
  if (progress[slug] === "solved") return;
  progress[slug] = accepted ? "solved" : "attempted";
  write(PROGRESS_KEY, JSON.stringify(progress));
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

function subscribe(onChange: () => void) {
  window.addEventListener("storage", onChange); // other tabs
  window.addEventListener(CHANGE_EVENT, onChange); // this tab
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(CHANGE_EVENT, onChange);
  };
}

export function useProgress(): Record<string, ProblemStatus> {
  const raw = useSyncExternalStore(
    subscribe,
    () => read(PROGRESS_KEY),
    () => null, // server render: nothing solved yet
  );
  return useMemo(() => parseProgress(raw), [raw]);
}
