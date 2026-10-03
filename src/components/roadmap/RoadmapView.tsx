"use client";

import { useCallback, useMemo, useState } from "react";
import type { ProblemStatus, ProblemSummary } from "@/lib/queries";
import { patterns, ROADMAP_ROWS, type Pattern } from "@/lib/roadmap";
import PatternDrawer from "./PatternDrawer";

const ROW_HEIGHT = 112;
const NODE_WIDTH = 140;
const NODE_HEIGHT = 56;

interface Props {
  problems: ProblemSummary[];
  statuses: Record<string, ProblemStatus>;
  signedIn: boolean;
}

export default function RoadmapView({ problems, statuses, signedIn }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const close = useCallback(() => setSelectedId(null), []);

  const patternsById = useMemo(() => new Map(patterns.map((p) => [p.id, p])), []);
  const problemsByPattern = useMemo(() => {
    const map = new Map<string, ProblemSummary[]>();
    for (const p of problems) map.set(p.pattern, [...(map.get(p.pattern) ?? []), p]);
    return map;
  }, [problems]);
  const childrenOf = useCallback((id: string) => patterns.filter((p) => p.parents.includes(id)), []);

  const progress = (p: Pattern) => {
    const list = problemsByPattern.get(p.id) ?? [];
    return { solved: list.filter((q) => statuses[q.slug] === "solved").length, total: list.length };
  };

  const selected = selectedId ? (patternsById.get(selectedId) ?? null) : null;
  const top = (row: number) => row * ROW_HEIGHT + 8;

  return (
    <>
      {/* Tree diagram (tablet and up) */}
      <div className="hidden overflow-x-auto rounded-lg border border-line bg-surface md:block">
        <div className="relative mx-auto min-w-[980px]" style={{ height: ROADMAP_ROWS * ROW_HEIGHT }}>
          <svg className="pointer-events-none absolute inset-0 h-full w-full" aria-hidden="true">
            {patterns.flatMap((child) =>
              child.parents.map((parentId) => {
                const parent = patternsById.get(parentId)!;
                const active = selectedId !== null && (selectedId === child.id || selectedId === parentId);
                return (
                  <line
                    key={`${parentId}-${child.id}`}
                    x1={`${parent.x}%`}
                    y1={top(parent.row) + NODE_HEIGHT}
                    x2={`${child.x}%`}
                    y2={top(child.row)}
                    className={active ? "stroke-accent-fill" : "stroke-line"}
                    strokeWidth={active ? 2.5 : 1.5}
                  />
                );
              }),
            )}
          </svg>

          {patterns.map((p) => {
            const { solved, total } = progress(p);
            const done = total > 0 && solved === total;
            return (
              <button
                key={p.id}
                onClick={() => setSelectedId(p.id)}
                aria-haspopup="dialog"
                className={`absolute flex flex-col justify-center rounded-lg border px-3 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md ${
                  selectedId === p.id
                    ? "border-accent-fill bg-surface ring-2 ring-accent-fill/40"
                    : done
                      ? "border-easy/60 bg-surface"
                      : "border-line bg-surface hover:border-accent-fill/60"
                }`}
                style={{
                  left: `calc(${p.x}% - ${NODE_WIDTH / 2}px)`,
                  top: top(p.row),
                  width: NODE_WIDTH,
                  height: NODE_HEIGHT,
                }}
              >
                <span className="truncate text-[12.5px] font-medium">{p.name}</span>
                <span className="mt-1.5 flex items-center gap-2">
                  <span className="h-1 flex-1 overflow-hidden rounded-full bg-surface-2">
                    <span className="block h-full rounded-full bg-easy" style={{ width: `${total ? (solved / total) * 100 : 0}%` }} />
                  </span>
                  <span className="text-[10px] text-muted">
                    {solved}/{total}
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* List (phones) */}
      <ol className="space-y-2 md:hidden">
        {patterns.map((p, i) => {
          const { solved, total } = progress(p);
          return (
            <li key={p.id}>
              <button
                onClick={() => setSelectedId(p.id)}
                className="flex w-full items-center gap-3 rounded-lg border border-line bg-surface px-4 py-3 text-left"
              >
                <span className="w-6 text-xs text-muted">{i + 1}</span>
                <span className="min-w-0 flex-1 truncate text-sm font-medium">{p.name}</span>
                <span className="text-xs text-muted">
                  {solved}/{total}
                </span>
              </button>
            </li>
          );
        })}
      </ol>

      <PatternDrawer
        pattern={selected}
        patternsById={patternsById}
        childrenOf={childrenOf}
        problems={selected ? (problemsByPattern.get(selected.id) ?? []) : []}
        statuses={statuses}
        signedIn={signedIn}
        onSelect={setSelectedId}
        onClose={close}
      />
    </>
  );
}
