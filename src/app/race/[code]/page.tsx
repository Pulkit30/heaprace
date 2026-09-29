import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import RaceRoom from "@/components/race/RaceRoom";
import { getCurrentUser } from "@/lib/auth/server";
import { getRaceState, normalizeCode } from "@/lib/race";

export async function generateMetadata({ params }: PageProps<"/race/[code]">): Promise<Metadata> {
  return { title: `Race ${(await params).code.toUpperCase()}` };
}

export default async function RacePage({ params }: PageProps<"/race/[code]">) {
  const raw = (await params).code;
  const code = normalizeCode(raw);
  if (!code) notFound();
  if (code !== raw) redirect(`/race/${code}`);

  const user = await getCurrentUser();
  if (!user) redirect(`/auth/sign-in?next=${encodeURIComponent(`/race/${code}`)}`);

  const state = await getRaceState(code, user.id);
  if (!state) notFound();
  // Remount when the viewer joins, so the room switches from "Join" to the player view immediately.
  return <RaceRoom key={`${state.code}:${state.isParticipant}`} initial={state} />;
}
