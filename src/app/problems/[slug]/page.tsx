import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getProblem, problems } from "@/lib/problems";
import Workspace from "@/components/workspace/Workspace";

export function generateStaticParams() {
  return problems.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: PageProps<"/problems/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  return { title: getProblem(slug)?.title ?? "Problem not found" };
}

export default async function ProblemPage({ params }: PageProps<"/problems/[slug]">) {
  const { slug } = await params;
  const problem = getProblem(slug);
  if (!problem) notFound();
  return <Workspace problem={problem} />;
}
