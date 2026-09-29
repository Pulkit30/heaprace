import type { Metadata } from "next";
import { redirect } from "next/navigation";
import ProgressView from "@/components/progress/ProgressView";
import { getCurrentUser } from "@/lib/auth/server";
import { getActivity, getSolvedByDifficulty } from "@/lib/queries";
import { getRaceStats } from "@/lib/race";
import { computeStreaks, todayIn } from "@/lib/streak";
import { getUserTimeZone } from "@/lib/timezone";

export const metadata: Metadata = { title: "My progress" };

export default async function ProgressPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/auth/sign-in?next=/progress");

  const timeZone = await getUserTimeZone();
  const today = todayIn(timeZone);
  const [activity, progress, raceStats] = await Promise.all([
    getActivity(user.id, timeZone),
    getSolvedByDifficulty(user.id),
    getRaceStats(user.id),
  ]);

  return (
    <ProgressView
      name={user.name || user.email}
      activity={activity}
      today={today}
      streak={computeStreaks(activity, today)}
      progress={progress}
      raceStats={raceStats}
    />
  );
}
