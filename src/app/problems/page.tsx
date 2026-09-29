import type { Metadata } from "next";
import { allTags, problems } from "@/lib/problems";
import ProblemTable, { type ProblemSummary } from "@/components/ProblemTable";

export const metadata: Metadata = { title: "Problems" };

export default function ProblemsPage() {
  // Only send what the list needs; test cases stay out of this page's payload.
  const summaries: ProblemSummary[] = problems.map(({ id, slug, title, difficulty, tags }) => ({
    id,
    slug,
    title,
    difficulty,
    tags,
  }));

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">Problems</h1>
      <p className="mt-1 text-sm text-muted">Pick one and start climbing.</p>
      <ProblemTable problems={summaries} tags={allTags} />
    </main>
  );
}
