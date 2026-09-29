import type { Metadata } from "next";
import { redirect } from "next/navigation";
import AuthForm from "@/components/auth/AuthForm";
import { getCurrentUser, safeNext } from "@/lib/auth/server";

export const metadata: Metadata = { title: "Sign in" };

export default async function SignInPage({ searchParams }: PageProps<"/auth/sign-in">) {
  const next = safeNext((await searchParams).next);
  if (await getCurrentUser()) redirect(next);
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-12">
      <AuthForm mode="sign-in" next={next} />
    </main>
  );
}
