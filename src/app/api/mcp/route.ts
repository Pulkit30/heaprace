import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";
import { getProblem, listProblems } from "@/lib/queries";
import { patterns } from "@/lib/roadmap";
import { explainError, getHint, getPattern, getPatternForProblem, getProblemNotes, HINT_LEVELS, searchKnowledge } from "@/lib/tutor/tools";

// HeapRace MCP server (Streamable HTTP, stateless). Any MCP client, such as Claude Desktop, Cursor or VS Code,
// can connect to https://<site>/api/mcp and tutor with HeapRace's problems, hints and knowledge base.
// Read-only and public: it exposes the same tools as the in-app tutor, never hidden tests or solutions.

const INSTRUCTIONS = `You are connected to HeapRace, a DSA practice platform. Use these tools to TUTOR the learner, not to solve problems for them.
- Never write a complete solution. Guide with questions, the pattern, and one hint at a time (get_hint level 1, then 2, then 3).
- Use explain_error when the learner shares an error or verdict, and search_knowledge for concepts.
- Point the learner to https://heaprace.vercel.app/problems/<slug> to write and run their code.`;

const text = (value: unknown) => ({
  content: [{ type: "text" as const, text: typeof value === "string" ? value : JSON.stringify(value, null, 2) }],
});

function buildServer(): McpServer {
  const server = new McpServer({ name: "heaprace", version: "1.0.0" }, { instructions: INSTRUCTIONS });

  server.registerTool(
    "list_problems",
    {
      title: "List problems",
      description: "List HeapRace problems with difficulty, topics and roadmap pattern. Optionally filter by difficulty or pattern id.",
      inputSchema: {
        difficulty: z.enum(["Easy", "Medium", "Hard"]).optional(),
        pattern: z.string().optional().describe("Roadmap pattern id, e.g. sliding-window (see list_patterns)"),
      },
      annotations: { readOnlyHint: true },
    },
    async ({ difficulty, pattern }) => {
      const all = await listProblems();
      return text(all.filter((p) => (!difficulty || p.difficulty === difficulty) && (!pattern || p.pattern === pattern)));
    },
  );

  server.registerTool(
    "get_problem",
    {
      title: "Get a problem",
      description: "The statement, examples, constraints, starter code and sample tests of a problem. Hidden tests are never included.",
      inputSchema: { slug: z.string().describe("Problem slug, e.g. two-sum") },
      annotations: { readOnlyHint: true },
    },
    async ({ slug }) => {
      const p = await getProblem(slug);
      if (!p) return { ...text(`No problem with slug "${slug}". Use list_problems.`), isError: true };
      return text({
        slug: p.slug,
        title: p.title,
        difficulty: p.difficulty,
        tags: p.tags,
        description: p.description,
        examples: p.examples,
        constraints: p.constraints,
        starterCode: p.starterCode,
        sampleTests: p.tests.filter((t) => t.sample).map(({ args, expected }) => ({ args, expected })),
        url: `https://heaprace.vercel.app/problems/${p.slug}`,
      });
    },
  );

  server.registerTool(
    "get_hint",
    {
      title: "Get a hint",
      description: `Progressive hint ${1}–${HINT_LEVELS} for a problem. Start at level 1 and only go further if the learner is still stuck.`,
      inputSchema: {
        slug: z.string(),
        level: z.number().int().min(1).max(HINT_LEVELS),
      },
      annotations: { readOnlyHint: true },
    },
    async ({ slug, level }) => {
      const hint = await getHint(slug, level);
      if (!hint) return { ...text(`No hint ${level} for "${slug}".`), isError: true };
      const extra = level === HINT_LEVELS ? await getProblemNotes(slug, "insight") : [];
      return text({ hint: hint.body, level, of: HINT_LEVELS, keyIdea: extra[0]?.body });
    },
  );

  server.registerTool(
    "search_knowledge",
    {
      title: "Search the knowledge base",
      description:
        "Full-text search over HeapRace's notes: pattern explanations, target complexities, common mistakes and error guides. Optionally scope to one problem.",
      inputSchema: { query: z.string().min(1), slug: z.string().optional() },
      annotations: { readOnlyHint: true },
    },
    async ({ query, slug }) => text(await searchKnowledge(query, { slug, limit: 5 })),
  );

  server.registerTool(
    "explain_error",
    {
      title: "Explain an error",
      description: "Explain a Python traceback or a verdict (Wrong Answer, Time Limit Exceeded...) and how to debug it.",
      inputSchema: { error: z.string().min(1).describe("The error text or verdict") },
      annotations: { readOnlyHint: true },
    },
    async ({ error }) => text(await explainError(error)),
  );

  server.registerTool(
    "list_patterns",
    {
      title: "List roadmap patterns",
      description: "The roadmap patterns in learning order, with prerequisites and how many problems each has.",
      inputSchema: {},
      annotations: { readOnlyHint: true },
    },
    async () => {
      const all = await listProblems();
      return text(
        patterns.map(({ id, name, parents }) => ({
          id,
          name,
          learnFirst: parents,
          problems: all.filter((p) => p.pattern === id).map((p) => p.slug),
        })),
      );
    },
  );

  server.registerTool(
    "get_pattern",
    {
      title: "Explain a pattern",
      description: "Explain a roadmap pattern (what it is, when to use it, how to apply it). Pass a pattern id, or a problem slug to get that problem's pattern.",
      inputSchema: { pattern: z.string().optional(), slug: z.string().optional() },
      annotations: { readOnlyHint: true },
    },
    async ({ pattern, slug }) => {
      const hit = pattern ? await getPattern(pattern) : slug ? await getPatternForProblem(slug) : null;
      if (!hit) return { ...text("Pattern not found. Use list_patterns."), isError: true };
      return text({ name: hit.title, explanation: hit.body });
    },
  );

  return server;
}

// Stateless: a fresh server and transport per request, so it works on serverless hosts.
async function handle(req: Request): Promise<Response> {
  const server = buildServer();
  const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
  await server.connect(transport);
  return transport.handleRequest(req);
}

export { handle as GET, handle as POST, handle as DELETE };
