"use server";

import { redirect } from "next/navigation";
import { auth, safeNext } from "@/lib/auth/server";

export type AuthFormState = { error: string } | null;

const field = (formData: FormData, name: string) => String(formData.get(name) ?? "").trim();

export async function signInWithEmail(_prev: AuthFormState, formData: FormData): Promise<AuthFormState> {
  const { error } = await auth.signIn.email({
    email: field(formData, "email"),
    password: String(formData.get("password") ?? ""),
  });
  if (error) return { error: error.message || "Could not sign in. Check your email and password." };
  redirect(safeNext(formData.get("next")));
}

export async function signUpWithEmail(_prev: AuthFormState, formData: FormData): Promise<AuthFormState> {
  const name = field(formData, "name");
  const email = field(formData, "email");
  const password = String(formData.get("password") ?? "");
  if (!name) return { error: "Please enter your name." };
  if (password.length < 8) return { error: "Password must be at least 8 characters." };

  const { error } = await auth.signUp.email({ name, email, password });
  if (error) return { error: error.message || "Could not create your account." };
  redirect(safeNext(formData.get("next")));
}

export async function signOut() {
  await auth.signOut();
  redirect("/");
}
