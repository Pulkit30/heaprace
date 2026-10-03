"use client";

// Unsaved code drafts stay in the browser (per device), like LeetCode.
// Solved status and submissions live in the database (see src/lib/queries.ts).

const codeKey = (slug: string) => `heaprace:code:${slug}`;

export function loadCode(slug: string): string | null {
  migrateStorage();
  try {
    return localStorage.getItem(codeKey(slug));
  } catch {
    return null;
  }
}

export function saveCode(slug: string, code: string) {
  migrateStorage();
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

// Drafts and tutor hint progress are per browser, so they're tied to the account that wrote them.
// Switching accounts (or signing out) clears them, so one person never sees another's code.
const OWNER_KEY = "heaprace:owner";
const PER_USER_PREFIXES = ["heaprace:code:", "heaprace:hints:"];

// Drafts saved before ownership existed can't be attributed to anyone, so they're removed once.
const STORAGE_VERSION_KEY = "heaprace:storage-version";
const STORAGE_VERSION = "2";

/** One-time cleanup of drafts written by older versions of the site. Safe to call often. */
export function migrateStorage() {
  try {
    if (localStorage.getItem(STORAGE_VERSION_KEY) === STORAGE_VERSION) return;
    for (const key of Object.keys(localStorage)) {
      if (PER_USER_PREFIXES.some((p) => key.startsWith(p))) localStorage.removeItem(key);
    }
    localStorage.setItem(STORAGE_VERSION_KEY, STORAGE_VERSION);
  } catch {
    // Storage blocked: nothing to migrate.
  }
}

/** Removes every code draft and hint-progress entry in this browser. */
export function clearUserData() {
  try {
    for (const key of Object.keys(localStorage)) {
      if (PER_USER_PREFIXES.some((p) => key.startsWith(p))) localStorage.removeItem(key);
    }
    localStorage.removeItem(OWNER_KEY);
  } catch {
    // Storage blocked: nothing was stored either.
  }
}

/** Marks this browser's drafts as belonging to `userId`, clearing them first if another account wrote them. */
export function claimUserData(userId: string) {
  migrateStorage();
  try {
    const owner = localStorage.getItem(OWNER_KEY);
    if (owner && owner !== userId) clearUserData();
    localStorage.setItem(OWNER_KEY, userId);
  } catch {
    // ignore
  }
}
