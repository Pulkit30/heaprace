"use client";

import Link from "next/link";
import { useState } from "react";
import type { SubmissionRow } from "@/lib/queries";
import TimeAgo from "../TimeAgo";
import VerdictText from "../VerdictText";

interface Props {
  submissions: SubmissionRow[];
  signedIn: boolean;
  signInHref: string;
  onLoadCode: (code: string) => void;
}

export default function SubmissionsPanel({ submissions, signedIn, signInHref, onLoadCode }: Props) {
  const [openId, setOpenId] = useState<number | null>(null);

  if (!signedIn) {
    return (
      <p className="p-5 text-sm text-muted">
        <Link href={signInHref} className="text-accent hover:underline">
          Sign in
        </Link>{" "}
        to save your submissions and see them here.
      </p>
    );
  }
  if (submissions.length === 0) {
    return <p className="p-5 text-sm text-muted">No submissions yet. Press Submit to judge your code against every test.</p>;
  }

  return (
    <ul className="divide-y divide-line">
      {submissions.map((s) => {
        const open = openId === s.id;
        return (
          <li key={s.id}>
            <button
              onClick={() => setOpenId(open ? null : s.id)}
              aria-expanded={open}
              className="flex w-full items-center gap-3 px-5 py-3 text-left text-sm transition-colors hover:bg-surface-2"
            >
              <span className="min-w-0 flex-1">
                <VerdictText verdict={s.verdict} className="font-medium" />
                <span className="block text-xs text-muted">
                  <TimeAgo iso={s.createdAt} />
                </span>
              </span>
              <span className="text-xs text-muted">
                {s.passed}/{s.total} tests
              </span>
              <span className="w-16 text-right text-xs text-muted">{s.runtimeMs} ms</span>
            </button>
            {open && (
              <div className="px-5 pb-4">
                <pre className="max-h-80 overflow-auto rounded-md border border-line bg-surface-2 p-3 font-mono text-[12.5px] leading-relaxed">
                  {s.code}
                </pre>
                <button
                  onClick={() => onLoadCode(s.code)}
                  className="mt-2 rounded-md border border-line px-3 py-1 text-xs text-muted transition-colors hover:text-fg"
                >
                  Load into editor
                </button>
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
