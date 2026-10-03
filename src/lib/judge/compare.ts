import type { CompareMode } from "../problems";

function deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.length === b.length && a.every((x, i) => deepEqual(x, b[i]));
  }
  if (a && b && typeof a === "object" && typeof b === "object") {
    const ka = Object.keys(a);
    const kb = Object.keys(b);
    return (
      ka.length === kb.length &&
      ka.every((k) => deepEqual((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k]))
    );
  }
  return false;
}

const sortByJson = (xs: unknown[]) => [...xs].sort((x, y) => (JSON.stringify(x) < JSON.stringify(y) ? -1 : 1));

/** Like deepEqual, but numbers may differ by a relative 1e-5 (answers that are decimals). */
function approxEqual(a: unknown, b: unknown): boolean {
  if (typeof a === "number" && typeof b === "number") return Math.abs(a - b) <= 1e-5 * Math.max(1, Math.abs(b));
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => approxEqual(x, b[i]));
  return deepEqual(a, b);
}

export function isCorrect(actual: unknown, expected: unknown, mode: CompareMode): boolean {
  if (mode === "approx") return approxEqual(actual, expected);
  if (mode === "exact" || !Array.isArray(actual) || !Array.isArray(expected)) {
    return deepEqual(actual, expected);
  }
  if (mode === "unordered-deep") {
    const inner = (xs: unknown[]) => xs.map((x) => (Array.isArray(x) ? sortByJson(x) : x));
    return deepEqual(sortByJson(inner(actual)), sortByJson(inner(expected)));
  }
  return deepEqual(sortByJson(actual), sortByJson(expected));
}

/** Python-style rendering so results look like what the user's code returned. */
export function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "None";
  if (v === true) return "True";
  if (v === false) return "False";
  if (typeof v === "string") return JSON.stringify(v);
  if (Array.isArray(v)) return `[${v.map(formatValue).join(", ")}]`;
  if (typeof v === "object") {
    return `{${Object.entries(v).map(([k, x]) => `${JSON.stringify(k)}: ${formatValue(x)}`).join(", ")}}`;
  }
  return String(v);
}
