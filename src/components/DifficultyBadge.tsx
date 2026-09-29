import type { Difficulty } from "@/lib/problems";

const styles: Record<Difficulty, string> = {
  Easy: "text-easy",
  Medium: "text-medium",
  Hard: "text-hard",
};

export default function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  return <span className={`text-sm font-medium ${styles[difficulty]}`}>{difficulty}</span>;
}
