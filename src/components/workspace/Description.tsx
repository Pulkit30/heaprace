import type { Problem } from "@/lib/problems";
import DifficultyBadge from "../DifficultyBadge";
import RichText from "../RichText";

export default function Description({ problem }: { problem: Problem }) {
  return (
    <article className="p-5">
      <h1 className="text-xl font-semibold tracking-tight">
        {problem.id}. {problem.title}
      </h1>
      <div className="mt-3 mb-6 flex flex-wrap items-center gap-2">
        <DifficultyBadge difficulty={problem.difficulty} />
        {problem.tags.map((t) => (
          <span key={t} className="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">
            {t}
          </span>
        ))}
      </div>

      <RichText text={problem.description} />

      {problem.examples.map((ex, i) => (
        <section key={i} className="mt-5">
          <h2 className="mb-2 text-sm font-semibold">Example {i + 1}</h2>
          <div className="space-y-1 border-l-2 border-line pl-4 font-mono text-[13px]">
            <p>
              <span className="text-muted">Input: </span>
              {ex.input}
            </p>
            <p>
              <span className="text-muted">Output: </span>
              {ex.output}
            </p>
            {ex.explanation && (
              <p className="font-sans text-sm">
                <span className="text-muted">Explanation: </span>
                {ex.explanation}
              </p>
            )}
          </div>
        </section>
      ))}

      <section className="mt-6">
        <h2 className="mb-2 text-sm font-semibold">Constraints</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm">
          {problem.constraints.map((c) => (
            <li key={c}>
              <code className="inline-code">{c}</code>
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
