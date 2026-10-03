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
| `npm run db:seed` | Load the hand-written problems and the `content/catalog` problems into the database (safe to re-run) |
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
| `kb_chunks` | The AI tutor's knowledge base: hints, key ideas, complexity targets, mistakes, pattern notes, error guides, with a full-text search index |
| `neon_auth.*` | Users and sessions, managed by Neon Auth |

Code drafts are kept in the browser (localStorage), like LeetCode.

## Adding a problem

There are two kinds of problems:

- **Hand-written (the original 31):** add an entry to `src/lib/problems.ts` (mark a few tests `sample: true`) and a reference solution to `scripts/reference_solutions.py`, registered in `REFERENCE`.
- **Catalog (everything else, organized by pattern):** add a function decorated with `@problem(...)` to a file in `content/catalog/`. The decorated function is the reference solution. Give it samples, extra tests and/or a `gen` input generator, and ideally a `brute` force to cross-check against. `content/build_catalog.py` computes every expected output, checks the hints, and assigns a stable id in `content/ids.json` (commit that file).

Extra hidden tests live next to the problems: each `content/catalog/*.py` file has an `EXTRA` dict (and `content/basics_extra.py` covers the hand-written 31) with:

- `edge`: hand-picked edge cases, cross-checked against the brute force;
- `edge_nb`: boundary cases too big for the brute force;
- `large`: near-limit inputs so slow (e.g. O(n²)) solutions time out. The reference must finish within 0.35 s locally, and each input is capped at about 150 KB.

The build requires at least 6 hidden tests per problem.

Then run `npm run verify:problems`, then `npm run db:seed`.

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
- **Extras**: streaks and activity calendar, a 28-pattern roadmap (`src/lib/roadmap.ts`), and the AI Tutor with RAG, agent and MCP
- **Phase 5**: launch on Vercel with a domain, own Google OAuth keys and SMTP, self-hosted Judge0

## AI Tutor (RAG + agent + MCP, no paid LLM)

Every problem page has an **✨ AI Tutor** tab (disabled in races). It never writes solutions; the knowledge base contains no code, and `npm run verify:problems` fails if code sneaks in.

- **RAG:** `src/lib/tutor/knowledge.ts` (3 progressive hints, key idea, complexity target and common mistakes per problem, plus pattern notes and Python error guides) is loaded into `kb_chunks` by `npm run db:seed` and retrieved with Postgres full-text search (weighted `tsvector` + GIN index, OR-ranked with `ts_rank_cd`).
- **Agent:** `src/lib/tutor/engine.ts` classifies the question, plans which tools to call (inspect the latest Run/Submit result, explain an error, retrieve notes, reveal the next hint, look up the pattern), runs them and composes a grounded reply. The UI shows each step and the sources. It runs without an LLM, so it costs nothing.
- **Tools:** `src/lib/tutor/tools.ts`, shared by the in-app agent and the MCP server.
- **MCP server:** `https://heaprace.vercel.app/api/mcp` (Streamable HTTP, stateless, read-only). Tools: `list_problems`, `get_problem`, `get_hint`, `search_knowledge`, `explain_error`, `list_patterns`, `get_pattern`, with server instructions to tutor rather than solve.

Connect an AI assistant:

```jsonc
// Cursor: .cursor/mcp.json   (VS Code: .vscode/mcp.json with "servers" and "type": "http")
{ "mcpServers": { "heaprace": { "url": "https://heaprace.vercel.app/api/mcp" } } }

// Claude Desktop: claude_desktop_config.json (bridges the remote server over stdio)
{ "mcpServers": { "heaprace": { "command": "npx", "args": ["-y", "mcp-remote", "https://heaprace.vercel.app/api/mcp"] } } }
```

Try it with the MCP Inspector: `npx @modelcontextprotocol/inspector`, then connect to the URL above.

## Race mode

`/race` creates a room (difficulty and length) or joins one by its 6-character code. The host starts the race; after a 5-second countdown every player gets the same random problem, hidden until then. Submissions go through the server judge, and the first Accepted wins. The race ends when everyone has solved it or time runs out. Race pages poll `/api/race/[code]` every 1–2 seconds, which works on any host; it can move to WebSockets later without changing the data model.
