# HeapRace

Climb the heap: a DSA practice platform where you write Python in the browser and get judged against test cases.

## Stack

Next.js 16 · Tailwind · Monaco editor · Pyodide (Python in a Web Worker) · Neon Postgres + Drizzle ORM · Neon Auth (Managed Better Auth)

## Run locally

```bash
npm install
neon link --project-id <your-project-id> --branch production   # writes DATABASE_URL etc. to .env.local
cp .env.example .env                                           # then set NEON_AUTH_COOKIE_SECRET
npm run db:migrate
npm run db:seed
npm run dev
```

Open http://localhost:3000.

## Scripts

| Command | What it does |
| --- | --- |
| `npm run dev` | Start the dev server (copies the Python runtime into `public/pyodide` first) |
| `npm run build` | Production build |
| `npm run lint` | ESLint |
| `npm run verify:problems` | Check every test case against the reference solutions in `scripts/reference_solutions.py` |
| `npm run db:generate` | Create a migration after changing `src/db/schema.ts` |
| `npm run db:migrate` | Apply migrations (uses the direct, non-pooled connection) |
| `npm run db:seed` | Load `src/lib/problems.ts` into the database (safe to re-run) |
| `npm run db:studio` | Browse the database in Drizzle Studio |

## Data

| Table | Holds |
| --- | --- |
| `problems` | Title, description, examples, constraints, starter code, compare mode |
| `test_cases` | Arguments and expected output per problem, flagged sample or hidden |
| `submissions` | User, problem, code, verdict, tests passed, runtime, time |
| `neon_auth.*` | Users and sessions, managed by Neon Auth |

Code drafts are kept in the browser (localStorage), like LeetCode.

## Adding a problem

1. Add an entry to `src/lib/problems.ts` (mark a few tests `sample: true`).
2. Add a reference solution to `scripts/reference_solutions.py` and register it in `REFERENCE`.
3. `npm run verify:problems`, then `npm run db:seed`.

## How judging works (until Phase 3)

Code runs in a Web Worker with [Pyodide](https://pyodide.org) (CPython compiled to WebAssembly), served by the app itself.
Each test has a 3 second limit; on timeout the worker is killed and restarted.
**Run** uses sample tests; **Submit** uses all tests and stops at the first failure, then saves the result for signed-in users.
Because judging happens in the browser, hidden tests reach the client and results can be faked. Phase 3 moves Submit to a server-side judge.

## Roadmap

- **Phase 1** (done): problem list, editor, in-browser Python, verdicts
- **Phase 2** (done): Neon Postgres, sign in (email or Google), saved submissions, light/dark theme
- **Phase 3**: server-side judge (Judge0) for Submit, hidden tests stay on the server
- **Phase 4**: Race mode (1v1 rooms, live leaderboard), profiles and streaks
