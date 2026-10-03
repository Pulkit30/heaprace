"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import type { ProblemStatus, ProblemSummary } from "@/lib/queries";
import type { Pattern } from "@/lib/roadmap";
import DifficultyBadge from "../DifficultyBadge";

interface Props {
  pattern: Pattern | null;
  patternsById: Map<string, Pattern>;
  childrenOf: (id: string) => Pattern[];
  /** The selected pattern's problems, in order. */
  problems: ProblemSummary[];
  statuses: Record<string, ProblemStatus>;
  signedIn: boolean;
  onSelect: (id: string) => void;
  onClose: () => void;
}

/** Slides in from the left with the selected pattern's explanation and problems. */
export default function PatternDrawer({
  pattern,
  patternsById,
  childrenOf,
  problems,
  statuses,
  signedIn,
  onSelect,
  onClose,
}: Props) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const open = pattern !== null;

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const solved = problems.filter((p) => statuses[p.slug] === "solved").length;

  const chip = "rounded-full border border-line px-2.5 py-0.5 text-xs text-muted transition-colors hover:border-accent-fill hover:text-fg";

  return (
    <>
      <div
        onClick={onClose}
        aria-hidden="true"
        className={`fixed inset-x-0 top-14 bottom-0 z-30 bg-black/30 transition-opacity ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={pattern?.name ?? "Pattern"}
        aria-hidden={!open}
        inert={!open}
        className={`fixed top-14 bottom-0 left-0 z-40 flex w-full flex-col border-r border-line bg-surface shadow-xl transition-transform duration-200 sm:w-[400px] ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {pattern && (
          <>
            <div className="flex items-start gap-3 border-b border-line px-5 py-4">
              <div className="min-w-0 flex-1">
                <h2 className="text-lg font-semibold tracking-tight">{pattern.name}</h2>
                <p className="mt-0.5 text-xs text-muted">
                  {signedIn ? `${solved}/${problems.length} solved` : `${problems.length} problem${problems.length === 1 ? "" : "s"}`}
                </p>
              </div>
              <button
                ref={closeRef}
                onClick={onClose}
                aria-label="Close"
                className="flex h-8 w-8 items-center justify-center rounded-md text-muted transition-colors hover:bg-surface-2 hover:text-fg"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-5 py-4">
              {signedIn && problems.length > 0 && (
                <div className="mb-4 h-1.5 overflow-hidden rounded-full bg-surface-2">
                  <div className="h-full rounded-full bg-easy" style={{ width: `${(solved / problems.length) * 100}%` }} />
                </div>
              )}

              <p className="text-sm leading-relaxed">{pattern.summary}</p>
              <div className="mt-3 rounded-md border border-line bg-surface-2 px-3 py-2 text-sm">
                <span className="font-medium">Use it when: </span>
                <span className="text-muted">{pattern.useWhen}</span>
              </div>

              <h3 className="mt-6 mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Problems</h3>
              <ul className="divide-y divide-line overflow-hidden rounded-lg border border-line">
                {problems.map((p) => {
                  const status = statuses[p.slug];
                  return (
                    <li key={p.slug}>
                      <Link
                        href={`/problems/${p.slug}`}
                        className="flex items-center gap-3 px-3 py-2.5 text-sm transition-colors hover:bg-surface-2"
                      >
                        <span className="w-4 text-center" aria-label={status ?? "not started"}>
                          {status === "solved" ? (
                            <span className="text-easy">✓</span>
                          ) : status === "attempted" ? (
                            <span className="text-medium">◐</span>
                          ) : (
                            <span className="text-muted/50">○</span>
                          )}
                        </span>
                        <span className="min-w-0 flex-1 truncate">{p.title}</span>
                        <DifficultyBadge difficulty={p.difficulty} />
                      </Link>
                    </li>
                  );
                })}
              </ul>

              {pattern.parents.length > 0 && (
                <>
                  <h3 className="mt-6 mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Learn first</h3>
                  <div className="flex flex-wrap gap-2">
                    {pattern.parents.map((id) => (
                      <button key={id} onClick={() => onSelect(id)} className={chip}>
                        {patternsById.get(id)?.name}
                      </button>
                    ))}
                  </div>
                </>
              )}
              {childrenOf(pattern.id).length > 0 && (
                <>
                  <h3 className="mt-5 mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Unlocks next</h3>
                  <div className="flex flex-wrap gap-2">
                    {childrenOf(pattern.id).map((c) => (
                      <button key={c.id} onClick={() => onSelect(c.id)} className={chip}>
                        {c.name}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </>
        )}
      </aside>
    </>
  );
}
