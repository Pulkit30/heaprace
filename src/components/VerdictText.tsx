import type { Verdict } from "@/lib/judge/runner";

export const verdictColor: Record<Verdict, string> = {
  Accepted: "text-easy",
  "Wrong Answer": "text-hard",
  "Runtime Error": "text-hard",
  "Time Limit Exceeded": "text-medium",
};

export default function VerdictText({ verdict, className = "" }: { verdict: Verdict; className?: string }) {
  return <span className={`${verdictColor[verdict]} ${className}`}>{verdict}</span>;
}
