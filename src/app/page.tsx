import Link from "next/link";
import { problems } from "@/lib/problems";

const features = [
  { title: "Run Python instantly", body: "Your code runs right in the browser. No setup, no waiting in a queue." },
  { title: "Real verdicts", body: "Accepted, Wrong Answer, Runtime Error or Time Limit Exceeded, with the failing input shown." },
  { title: "Race mode (soon)", body: "Go head to head with friends on the same problem. First correct submission wins." },
];

export default function Home() {
  const counts = {
    Easy: problems.filter((p) => p.difficulty === "Easy").length,
    Medium: problems.filter((p) => p.difficulty === "Medium").length,
    Hard: problems.filter((p) => p.difficulty === "Hard").length,
  };

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-16 sm:py-24">
      <section className="max-w-2xl">
        <p className="mb-4 text-sm font-medium uppercase tracking-widest text-accent">Climb the heap</p>
        <h1 className="text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          Solve DSA problems. <br className="hidden sm:block" />
          Race to the top.
        </h1>
        <p className="mt-5 text-lg text-muted">
          Practice the problems that show up in coding interviews and placement tests, write Python in a real
          editor, and get judged against hidden test cases.
        </p>
        <div className="mt-8 flex flex-wrap items-center gap-4">
          <Link
            href="/problems"
            className="rounded-md bg-accent px-5 py-2.5 font-medium text-black transition-colors hover:bg-accent-strong"
          >
            Start solving
          </Link>
          <span className="text-sm text-muted">
            {problems.length} problems ·{" "}
            <span className="text-easy">{counts.Easy} easy</span> ·{" "}
            <span className="text-medium">{counts.Medium} medium</span> ·{" "}
            <span className="text-hard">{counts.Hard} hard</span>
          </span>
        </div>
      </section>

      <section className="mt-20 grid gap-4 sm:grid-cols-3">
        {features.map((f) => (
          <div key={f.title} className="rounded-lg border border-line bg-surface p-5">
            <h2 className="font-medium">{f.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-muted">{f.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
