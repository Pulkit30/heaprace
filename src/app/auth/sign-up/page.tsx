import type { Metadata } from "next";
import { redirect } from "next/navigation";
import AuthForm from "@/components/auth/AuthForm";
import { getCurrentUser, safeNext } from "@/lib/auth/server";

export const metadata: Metadata = { title: "Create account" };

export default async function SignUpPage({ searchParams }: PageProps<"/auth/sign-up">) {
  const next = safeNext((await searchParams).next);
  if (await getCurrentUser()) redirect(next);
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-12">
      <AuthForm mode="sign-up" next={next} />
    </main>
  );
}
