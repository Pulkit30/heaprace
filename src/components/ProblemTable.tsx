"use client";

import Link from "next/link";
import { useState } from "react";
import type { Difficulty } from "@/lib/problems";
import type { ProblemStatus, ProblemSummary } from "@/lib/queries";
import DifficultyBadge from "./DifficultyBadge";

const difficulties: (Difficulty | "All")[] = ["All", "Easy", "Medium", "Hard"];

const PAGE_SIZE = 50;

interface Props {
  problems: ProblemSummary[];
  tags: string[];
  /** Roadmap patterns in learning order, for the pattern filter. */
  patterns: { id: string; name: string }[];
  statuses: Record<string, ProblemStatus>;
  showProgress: boolean;
}

export default function ProblemTable({ problems, tags, patterns, statuses: progress, showProgress }: Props) {
  const [query, setQuery] = useState("");
  const [difficulty, setDifficulty] = useState<Difficulty | "All">("All");
  const [tag, setTag] = useState("All");
  const [pattern, setPattern] = useState("All");
  const [page, setPage] = useState(0);

  const q = query.trim().toLowerCase();
  const matching = problems.filter(
    (p) =>
      (difficulty === "All" || p.difficulty === difficulty) &&
      (tag === "All" || p.tags.includes(tag)) &&
      (pattern === "All" || p.pattern === pattern) &&
      (!q || p.title.toLowerCase().includes(q) || String(p.id) === q),
  );
  const pages = Math.max(1, Math.ceil(matching.length / PAGE_SIZE));
  const current = Math.min(page, pages - 1);
  const visible = matching.slice(current * PAGE_SIZE, (current + 1) * PAGE_SIZE);
  // Any filter change starts again from the first page.
  const filter =
    <T,>(set: (v: T) => void) =>
    (v: T) => {
      set(v);
      setPage(0);
    };
  const solved = problems.filter((p) => progress[p.slug] === "solved").length;

  const selectClass =
    "rounded-md border border-line bg-surface px-3 py-2 text-sm outline-none focus:border-accent-fill";

  return (
    <>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <input
          value={query}
          onChange={(e) => filter(setQuery)(e.target.value)}
          placeholder="Search problems"
          aria-label="Search problems"
          className={`${selectClass} min-w-0 flex-1 basis-56 placeholder:text-muted`}
        />
        <select
          value={difficulty}
          onChange={(e) => filter(setDifficulty)(e.target.value as Difficulty | "All")}
          aria-label="Difficulty"
          className={selectClass}
        >
          {difficulties.map((d) => (
            <option key={d} value={d}>
              {d === "All" ? "All difficulties" : d}
            </option>
          ))}
        </select>
        <select value={pattern} onChange={(e) => filter(setPattern)(e.target.value)} aria-label="Pattern" className={selectClass}>
          <option value="All">All patterns</option>
          {patterns.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <select value={tag} onChange={(e) => filter(setTag)(e.target.value)} aria-label="Tag" className={selectClass}>
          <option value="All">All topics</option>
          {tags.map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
        {showProgress && (
          <span className="text-sm text-muted">
            <span className="font-medium text-fg">{solved}</span>/{problems.length} solved
          </span>
        )}
      </div>

      <div className="mt-4 overflow-hidden rounded-lg border border-line">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="w-12 px-4 py-3 font-medium">
                <span className="sr-only">Status</span>
              </th>
              <th className="px-4 py-3 font-medium">Title</th>
              <th className="w-28 px-4 py-3 font-medium">Difficulty</th>
              <th className="hidden px-4 py-3 font-medium md:table-cell">Topics</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((p) => {
              const status = progress[p.slug];
              return (
                <tr key={p.slug} className="border-t border-line transition-colors hover:bg-surface">
                  <td className="px-4 py-3">
                    {status === "solved" && (
                      <span className="text-easy" title="Solved">
                        ✓
                      </span>
                    )}
                    {status === "attempted" && (
                      <span className="text-medium" title="Attempted">
                        ◐
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <Link href={`/problems/${p.slug}`} className="hover:text-accent">
                      {p.id}. {p.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <DifficultyBadge difficulty={p.difficulty} />
                  </td>
                  <td className="hidden px-4 py-3 md:table-cell">
                    <div className="flex flex-wrap gap-1.5">
                      {p.tags.map((t) => (
                        <span key={t} className="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
            {visible.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-muted">
                  No problems match those filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {pages > 1 && (
        <div className="mt-4 flex items-center justify-between text-sm text-muted">
          <span>
            {current * PAGE_SIZE + 1}–{Math.min((current + 1) * PAGE_SIZE, matching.length)} of {matching.length}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(current - 1)}
              disabled={current === 0}
              className="rounded-md border border-line px-3 py-1.5 transition-colors hover:bg-surface-2 disabled:opacity-40"
            >
              ← Previous
            </button>
            <button
              onClick={() => setPage(current + 1)}
              disabled={current >= pages - 1}
              className="rounded-md border border-line px-3 py-1.5 transition-colors hover:bg-surface-2 disabled:opacity-40"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </>
  );
}
