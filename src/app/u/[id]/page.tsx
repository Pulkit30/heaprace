import type { Metadata } from "next";
import { notFound } from "next/navigation";
import ProgressView from "@/components/progress/ProgressView";
import { getCurrentUser } from "@/lib/auth/server";
import { getActivity, getPublicUser, getSolvedByDifficulty } from "@/lib/queries";
import { getRaceStats } from "@/lib/race";
import { computeStreaks, todayIn } from "@/lib/streak";
import { getUserTimeZone } from "@/lib/timezone";

export async function generateMetadata({ params }: PageProps<"/u/[id]">): Promise<Metadata> {
  const user = await getPublicUser((await params).id);
  return { title: user ? user.name : "Profile not found" };
}

/** Public profile: solved problems, streaks, activity calendar and race record. */
export default async function ProfilePage({ params }: PageProps<"/u/[id]">) {
  const { id } = await params;
  const [profile, viewer] = await Promise.all([getPublicUser(id), getCurrentUser()]);
  if (!profile) notFound();

  // Days are shown in the viewer's timezone.
  const timeZone = await getUserTimeZone();
  const today = todayIn(timeZone);
  const [activity, progress, raceStats] = await Promise.all([
    getActivity(profile.id, timeZone),
    getSolvedByDifficulty(profile.id),
    getRaceStats(profile.id),
  ]);

  return (
    <ProgressView
      title={profile.name}
      name={viewer?.id === profile.id ? "Your public profile" : "HeapRace profile"}
      image={profile.image}
      isOwn={viewer?.id === profile.id}
      activity={activity}
      today={today}
      streak={computeStreaks(activity, today)}
      progress={progress}
      raceStats={raceStats}
    />
  );
}
