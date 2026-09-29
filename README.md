# HeapRace

Climb the heap: a DSA practice platform where you write Python in the browser and get judged against test cases.

## Run locally

```bash
npm install
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

## Adding a problem (Phase 1)

1. Add an entry to `src/lib/problems.ts` (mark a few tests `sample: true`).
2. Add a reference solution to `scripts/reference_solutions.py` and register it in `REFERENCE`.
3. Run `npm run verify:problems`; it must pass.

## How judging works (Phase 1)

Code runs in a Web Worker with [Pyodide](https://pyodide.org) (CPython compiled to WebAssembly), served by the app itself.
Each test has a 3 second limit; on timeout the worker is killed and restarted.
**Run** uses sample tests; **Submit** uses all tests and stops at the first failure.
Because judging happens in the browser, results can be faked. Phase 3 moves Submit to a server-side judge.

## Roadmap

- **Phase 1** (done): problem list, editor, in-browser Python, verdicts, progress saved in the browser
- **Phase 2**: PostgreSQL + Prisma, sign in (Auth.js), submission history
- **Phase 3**: server-side judge (Judge0) for Submit
- **Phase 4**: Race mode (1v1 rooms, live leaderboard), profiles and streaks
