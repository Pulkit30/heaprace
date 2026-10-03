"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { askTutor } from "@/app/tutor/actions";
import { migrateStorage } from "@/lib/drafts";
import type { TutorAction, TutorReply, TutorResultContext } from "@/lib/tutor/engine";

const ACTION_LABEL: Record<TutorAction, string> = {
  hint: "💡 Give me a hint",
  debug: "🐞 Why is my code failing?",
  pattern: "🧭 Which pattern is this?",
  complexity: "⏱ Target complexity",
};

type Message = { role: "you"; text: string } | { role: "tutor"; reply: TutorReply } | { role: "error"; text: string };

const hintsKey = (slug: string) => `heaprace:hints:${slug}`;

function loadHints(slug: string): number {
  migrateStorage();
  try {
    return Number(localStorage.getItem(hintsKey(slug))) || 0;
  } catch {
    return 0;
  }
}

function saveHints(slug: string, n: number) {
  try {
    localStorage.setItem(hintsKey(slug), String(n));
  } catch {
    // Storage blocked: hint progress resets on reload.
  }
}

interface Props {
  slug: string;
  /** The latest Run or Submit result in this editor, so the tutor can explain it. */
  lastResult?: TutorResultContext;
}

export default function TutorPanel({ slug, lastResult }: Props) {
  // Rendered only after the tab is opened in the browser, so reading localStorage here is safe.
  const [hintsRevealed, setHintsRevealed] = useState(() => loadHints(slug));
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [pending, startTransition] = useTransition();
  const listRef = useRef<HTMLDivElement>(null);

  // Keep the newest message in view by scrolling the chat list only. (scrollIntoView would also
  // scroll the page and push the editor's Run/Submit bar out of sight.)
  useEffect(() => {
    const list = listRef.current;
    if (list && (messages.length > 0 || pending)) list.scrollTo({ top: list.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  function ask(message: string, action?: TutorAction) {
    const text = message.trim() || (action ? ACTION_LABEL[action].replace(/^\S+\s/, "") : "");
    if (!text || pending) return;
    setMessages((m) => [...m, { role: "you", text }]);
    setDraft("");
    startTransition(async () => {
      try {
        const res = await askTutor({ slug, message: text, action, hintsRevealed, lastResult });
        if ("error" in res) {
          setMessages((m) => [...m, { role: "error", text: res.error }]);
          return;
        }
        setHintsRevealed(res.hintsRevealed);
        saveHints(slug, res.hintsRevealed);
        setMessages((m) => [...m, { role: "tutor", reply: res }]);
      } catch {
        setMessages((m) => [...m, { role: "error", text: "The tutor is unavailable right now. Try again in a moment." }]);
      }
    });
  }

  const lastTutor = [...messages].reverse().find((m) => m.role === "tutor");
  const suggestions: TutorAction[] =
    lastTutor?.role === "tutor" ? lastTutor.reply.suggestions : ["hint", "debug", "pattern", "complexity"];

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div ref={listRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        <div className="rounded-lg border border-line bg-surface-2 p-3 text-sm">
          <p className="font-medium">AI Tutor</p>
          <p className="mt-1 text-muted">
            I guide you toward the answer without giving it away: progressive hints, the pattern behind the problem, the
            complexity to aim for, and why your last Run failed. I never write the solution.
          </p>
          <p className="mt-2 text-xs text-muted">
            Hints used: {hintsRevealed}/3
            {hintsRevealed > 0 && (
              <button
                onClick={() => {
                  setHintsRevealed(0);
                  saveHints(slug, 0);
                }}
                className="ml-2 text-accent hover:underline"
              >
                reset
              </button>
            )}
          </p>
        </div>

        {messages.map((m, i) =>
          m.role === "you" ? (
            <div key={i} className="flex justify-end">
              <p className="max-w-[85%] rounded-2xl rounded-br-sm bg-accent-fill/15 px-3 py-2 text-sm">{m.text}</p>
            </div>
          ) : m.role === "error" ? (
            <p key={i} className="text-sm text-hard">
              {m.text}
            </p>
          ) : (
            <TutorMessage key={i} reply={m.reply} />
          ),
        )}
        {pending && <p className="animate-pulse text-sm text-muted">Thinking through your question…</p>}
      </div>

      <div className="shrink-0 border-t border-line p-3">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {suggestions.map((a) => (
            <button
              key={a}
              onClick={() => ask("", a)}
              disabled={pending}
              className="rounded-full border border-line px-2.5 py-1 text-xs text-muted transition-colors hover:border-accent-fill hover:text-fg disabled:opacity-50"
            >
              {ACTION_LABEL[a]}
            </button>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask(draft);
          }}
          className="flex gap-2"
        >
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            maxLength={500}
            placeholder="Ask about this problem…"
            aria-label="Ask the tutor"
            className="min-w-0 flex-1 rounded-md border border-line bg-surface-2 px-3 py-2 text-sm outline-none placeholder:text-muted focus:border-accent-fill"
          />
          <button
            disabled={pending || !draft.trim()}
            className="rounded-md bg-accent-fill px-3 py-2 text-sm font-medium text-on-accent transition-colors hover:bg-accent-strong disabled:opacity-50"
          >
            Ask
          </button>
        </form>
      </div>
    </div>
  );
}

function TutorMessage({ reply }: { reply: TutorReply }) {
  return (
    <div className="space-y-2">
      <details className="text-xs text-muted">
        <summary className="cursor-pointer select-none hover:text-fg">
          How I got this ({reply.steps.length} step{reply.steps.length === 1 ? "" : "s"})
        </summary>
        <ol className="mt-1 list-decimal space-y-0.5 pl-5">
          {reply.steps.map((s, i) => (
            <li key={i}>
              <code className="inline-code">{s.tool}</code> {s.label}
            </li>
          ))}
        </ol>
      </details>

      {reply.blocks.map((b, i) => (
        <div
          key={i}
          className={`rounded-lg border px-3 py-2 text-sm ${b.style === "note" ? "border-transparent bg-transparent px-0 text-muted" : "border-line bg-surface"}`}
        >
          {b.title && <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">{b.title}</p>}
          {b.style === "code" ? (
            <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-[12.5px]">{b.text}</pre>
          ) : (
            <p className="whitespace-pre-wrap leading-relaxed">{b.text}</p>
          )}
        </div>
      ))}

      {reply.sources.length > 0 && (
        <p className="text-[11px] text-muted">
          Sources: {reply.sources.join(" · ")}
        </p>
      )}
    </div>
  );
}
