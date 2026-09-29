import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Workspace from "@/components/workspace/Workspace";
import { getCurrentUser } from "@/lib/auth/server";
import { getProblem, getProblemSubmissions } from "@/lib/queries";

export async function generateMetadata({ params }: PageProps<"/problems/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const problem = await getProblem(slug);
  return { title: problem?.title ?? "Problem not found" };
}

export default async function ProblemPage({ params }: PageProps<"/problems/[slug]">) {
  const { slug } = await params;
  const [problem, user] = await Promise.all([getProblem(slug), getCurrentUser()]);
  if (!problem) notFound();
  const submissions = user ? await getProblemSubmissions(user.id, problem.id) : [];

  // Only sample tests reach the browser (for Run). Submit is judged on the server with every test.
  const publicProblem = { ...problem, tests: problem.tests.filter((t) => t.sample) };
  return <Workspace problem={publicProblem} signedIn={!!user} initialSubmissions={submissions} />;
}
