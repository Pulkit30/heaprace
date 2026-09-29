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
| `npm run test:streak` | Unit tests for streak and date logic |

## Data

| Table | Holds |
| --- | --- |
| `problems` | Title, description, examples, constraints, starter code, compare mode |
| `test_cases` | Arguments and expected output per problem, flagged sample or hidden |
| `submissions` | User, problem, code, verdict, tests passed, runtime, time, and the race it belonged to (if any) |
| `race_rooms` | Race code, host, secret problem, difficulty, length, status, start and end time |
| `race_participants` | Who joined each race, their attempts, and when they solved it |
| `neon_auth.*` | Users and sessions, managed by Neon Auth |

Code drafts are kept in the browser (localStorage), like LeetCode.

## Adding a problem

1. Add an entry to `src/lib/problems.ts` (mark a few tests `sample: true`).
2. Add a reference solution to `scripts/reference_solutions.py` and register it in `REFERENCE`.
3. `npm run verify:problems`, then `npm run db:seed`.

## How judging works

- **Run** checks the sample tests in the browser: a Web Worker running [Pyodide](https://pyodide.org) (CPython compiled to WebAssembly), served by the app itself. 3 s per test; an infinite loop kills and restarts the worker.
- **Submit** is judged on the server (`src/app/problems/[slug]/actions.ts` → `src/lib/judge/server`). The browser only ever receives sample tests; hidden tests stay on the server, and the verdict can't be faked. Submitting needs an account and is limited to 10 submissions a minute.
- Both judges use the same Python harness (`src/lib/judge/harness.ts`), so Run and Submit behave identically. Linked lists and trees are built from JSON (`argTypes` / `returnType` on a problem).

### Judge backends

| Setting | Backend |
| --- | --- |
| `JUDGE0_URL` empty (development) | Your local `python3`, no sandbox. Refuses to run in production. |
| `JUDGE0_URL=http://your-server:2358` | Self-hosted [Judge0](https://github.com/judge0/judge0) (recommended for launch) |
| `JUDGE0_URL=https://judge0-ce.p.rapidapi.com` + `JUDGE0_RAPIDAPI_KEY` | Hosted Judge0 on RapidAPI (free tier is small) |

Self-hosting Judge0 on an Ubuntu server with Docker, following the official [deployment guide](https://github.com/judge0/judge0/blob/master/CHANGELOG.md#deployment-procedure): download the release, set `REDIS_PASSWORD`, `POSTGRES_PASSWORD` and `AUTHN_TOKEN` in `judge0.conf`, run `docker compose up -d db redis`, then `docker compose up -d`. Point `JUDGE0_URL` at port 2358 and set `JUDGE0_AUTH_TOKEN` to the `AUTHN_TOKEN`.

## Roadmap

- **Phase 1** (done): problem list, editor, in-browser Python, verdicts
- **Phase 2** (done): Neon Postgres, sign in (email or Google), saved submissions, light/dark theme
- **Phase 3** (done): server-side judge for Submit (Judge0, or local Python in development); hidden tests stay on the server
- **Phase 4** (done): Race mode (rooms up to 8 players, countdown, live standings, results) and public profiles
- **Extras**: streaks and activity calendar, a 28-pattern roadmap (`src/lib/roadmap.ts`)
- **Phase 5**: launch on Vercel with a domain, own Google OAuth keys and SMTP, self-hosted Judge0

## Race mode

`/race` creates a room (difficulty and length) or joins one by its 6-character code. The host starts the race; after a 5-second countdown every player gets the same random problem, hidden until then. Submissions go through the server judge, and the first Accepted wins. The race ends when everyone has solved it or time runs out. Race pages poll `/api/race/[code]` every 1–2 seconds, which works on any host; it can move to WebSockets later without changing the data model.
