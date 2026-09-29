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

  // Phase 2 still judges in the browser, so hidden tests are sent to the client. Phase 3 keeps them on the server.
  return <Workspace problem={problem} signedIn={!!user} initialSubmissions={submissions} />;
}
