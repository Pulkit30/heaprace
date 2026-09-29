"use client";

// Unsaved code drafts stay in the browser (per device), like LeetCode.
// Solved status and submissions live in the database (see src/lib/queries.ts).

const codeKey = (slug: string) => `heaprace:code:${slug}`;

export function loadCode(slug: string): string | null {
  try {
    return localStorage.getItem(codeKey(slug));
  } catch {
    return null;
  }
}

export function saveCode(slug: string, code: string) {
  try {
    localStorage.setItem(codeKey(slug), code);
  } catch {
    // Storage full or blocked (private mode): the draft just won't persist.
  }
}

export function clearCode(slug: string) {
  try {
    localStorage.removeItem(codeKey(slug));
  } catch {
    // ignore
  }
}
